import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QFileDialog, QProgressBar,
    QWidget, QComboBox, QMessageBox, QDialog, QPushButton, QMenuBar, QMenu, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon

class Translations:
    LANGUAGES = {
        'Turkish': {
            'app_title': "✨ SEFIDE ✨",
            'about_title': "Hakkında",
            'description': "SEcure FIle DEstructor",
            'security_level': "Güvenlik Seviyesi:",
            'security_levels': [
                "Hızlı (1 Geçiş)", 
                "Orta (3 Geçiş)", 
                "Yüksek (7 Geçiş)", 
                "Gutmann (35 Geçiş)"
            ],
            'drag_drop_label': "Dosya veya klasör sürükleyin ya da seçmek için herhangi bir yere tıklayın.",
            'not_started': "Henüz işlem yapılmadı",
            'processing_start': "İşlem başlıyor...",
            'processing_file': "Yok ediliyor: {}",
            'delete_success': "Dosya(lar) başarıyla yok edildi!",
            'delete_failed': "{} dosyası yok edilemedi!",
            'completion_message': "Tamamlandı",
            'ready': "Hazır",
            'about_text': (
                "SEFIDE\n"
                "(SEcure FIle DEstructor)\n\n"
                " SEFIDE, Dosyalarınızı güvenli bir şekilde kalıcı olarak yok etmeniz için tasarlanmış güçlü bir araçtır. Günümüzde, hassas bilgilerin ve dosyaların yanlış ellere geçmesi ciddi güvenlik sorunlarına yol açabilir. Bu uygulama, dijital güvenliğinizi sağlamak için geliştirilmiştir.\n\n"
                " Geliştirici: ALG Yazılım Inc. | www.algyzilim.com | info@algyazilim.com\n\n"
                " Fatih ÖNDER (CekToR) | wwww.fatihonder.org.tr | fatih@algyazilim.com\n\n"
                " EnCo Tüm Hakları Saklıdır. 2024 ALG Software Inc\n\n"
                " ALG Yazılım Pardus'a Göç'ü Destekler.\n\n"
                " SEFIDE Sürüm: 1.0\n\n"
            ),
            'close': "Kapat"
        },
        'English': {
            'app_title': "✨ SEFIDE ✨",
            'about_title': "About",
            'description': "SEcure FIle DEstructor",
            'security_level': "Security Level:",
            'security_levels': [
                "Fast (1 Pass)", 
                "Medium (3 Passes)", 
                "High (7 Passes)", 
                "Gutmann (35 Passes)"
            ],
            'drag_drop_label': "Drag and drop files or folders, or click anywhere to select.",
            'not_started': "No operation started yet",
            'processing_start': "Starting process...",
            'processing_file': "is being destroyed: {}",
            'delete_success': "File(s) successfully destroyed!",
            'delete_failed': "{} file could not be destroyed!",
            'completion_message': "Completed",
            'ready': "Ready",
            'about_text': (
                "SEFIDE\n"
                "(SEcure FIle DEstructor)\n\n"
                " SEFIDE is a powerful tool designed to securely and permanently destroy your files and folders. In today's world, sensitive information and files falling into the wrong hands can lead to serious security issues. This application is developed to ensure your digital security.\n\n"
                " Developer: ALG Software Inc. | www.algyzilim.com | info@algyazilim.com\n\n"
                " Fatih ÖNDER (CekToR) | wwww.fatihonder.org.tr | fatih@algyazilim.com\n\n"
                " EnCo All Rights Reserved. 2024 ALG Software Inc\n\n"
                " ALG Software Supports Migration to Pardus.\n\n"
                " SEFIDE Version: 1.0\n\n"
            ),
            'close': "Close"
        }
    }

    @classmethod
    def get_language(cls, language_name):
        return cls.LANGUAGES.get(language_name, cls.LANGUAGES['English'])

# Logo ve İkon Dosya Yolu Kontrolleri
def get_logo_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "sefidelo.png")
    elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/sefidelo.png"):
        return "/usr/share/icons/hicolor/48x48/apps/sefidelo.png"
    elif os.path.exists("sefidelo.png"):
        return "sefidelo.png"
    return None

def get_icon_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "sefidelo.png")
    elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/sefidelo.png"):
        return "/usr/share/icons/hicolor/48x48/apps/sefidelo.png"
    return None

LOGO_PATH = get_logo_path()
ICON_PATH = get_icon_path()

# Güvenli Silme Algoritması
def overwrite_file(path, passes=1):
    try:
        with open(path, "r+b") as file:
            length = os.path.getsize(path)
            for _ in range(passes):
                file.seek(0)
                file.write(bytearray(random.getrandbits(8) for _ in range(length)))
        os.remove(path)
    except Exception as e:
        print(f"Hata: {e}")
        return False
    return True

# "Hakkında" Penceresi
class AboutDialog(QDialog):
    def __init__(self, translation):
        super().__init__()
        self.translation = translation
        
        self.setWindowTitle(translation['about_title'])
        self.setWindowIcon(QIcon("sefidelo.png"))
        self.setFixedSize(400, 450)
        self.setStyleSheet("background-color: #1F1F1F; color: #FBB318;")

        about_layout = QVBoxLayout()
        about_label = QLabel(f"\n\n{translation['about_text']}")
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_label)

        close_button = QPushButton(translation['close'])
        close_button.clicked.connect(self.close)
        about_layout.addWidget(close_button)

        self.setLayout(about_layout)

# Güvenli Silme İşlemleri için Çalışma Thread'i
class DeleteFilesThread(QThread):
    progress_signal = pyqtSignal(int)
    complete_signal = pyqtSignal(str)
    current_file_signal = pyqtSignal(str)

    def __init__(self, file_paths, passes, translation):
        super().__init__()
        self.file_paths = file_paths
        self.passes = passes
        self.translation = translation

    def run(self):
        total_files = len(self.file_paths)
        for index, file in enumerate(self.file_paths):
            self.current_file_signal.emit(self.translation['processing_file'].format(os.path.basename(file)))
            
            if not overwrite_file(file, self.passes):
                self.complete_signal.emit(self.translation['delete_failed'].format(file))
            else:
                self.progress_signal.emit(int((index + 1) / total_files * 100))
        
        self.complete_signal.emit(self.translation['delete_success'])

# Ana Uygulama
class SecureDeleteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Language persistence
        self.language = self.load_language()
        self.translation = Translations.get_language(self.language)
        
        # Setup UI with current language
        self.setup_ui()

    def load_language(self):
        # Simple language persistence using a text file
        try:
            with open('language_preference.txt', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return 'Turkish'  # Default language

    def save_language(self, language):
        with open('language_preference.txt', 'w') as f:
            f.write(language)

    def change_language(self, language):
        self.language = language
        self.save_language(language)
        self.translation = Translations.get_language(language)
        self.setup_ui()

    def setup_ui(self):
        # Reset window to prevent duplicating widgets
        for widget in self.findChildren(QWidget):
            widget.deleteLater()

        self.setWindowTitle(self.translation['app_title'])
        self.setWindowIcon(QIcon("sefidelo.png"))
        self.setFixedSize(320, 550)
        self.setStyleSheet("background-color: #1F1F1F; color: #FBB318;")

        # Uygulama İkonunu Ayarlama
        if ICON_PATH:
            self.setWindowIcon(QIcon(ICON_PATH))

        # Create menu bar for language selection
        self.create_menu_bar()

        # Ana Widget ve Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # "Hakkında" tıklanabilir label
        about_label = QLabel("...")
        about_label.setStyleSheet("font-size: 15px; color: #f0a500;")
        about_label.setAlignment(Qt.AlignCenter)
        about_label.mousePressEvent = self.show_about_dialog
        main_layout.addWidget(about_label)

        # "SEFIDE" Başlık
        sefide_label = QLabel("SEFIDE")
        sefide_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0a500;")
        sefide_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(sefide_label)

        # Açıklama Etiketi
        description_label = QLabel(self.translation['description'])
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0a500;")
        description_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description_label)

        # Logo
        logo_label = QLabel()
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            logo_pixmap = QPixmap(LOGO_PATH)
            if logo_pixmap.isNull():
                logo_label.setText("Logo yüklenemedi")
            else:
                logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        else:
            logo_label.setText("Logo yüklenemedi")
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Güvenlik Seviyesi
        self.security_label = QLabel(self.translation['security_level'])
        self.security_combo = QComboBox()
        self.security_combo.addItems(self.translation['security_levels'])
        main_layout.addWidget(self.security_label)
        main_layout.addWidget(self.security_combo)

        # Güncel Dosya Etiketi
        self.current_file_label = QLabel(self.translation['not_started'])
        self.current_file_label.setStyleSheet("color: #FBB318;")
        self.current_file_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.current_file_label)

        # İlerleme Çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Mesaj Alanı
        self.drag_drop_label = QLabel(self.translation['drag_drop_label'])
        self.drag_drop_label.setWordWrap(True)
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.drag_drop_label)

        # Sürükle Bırak Etkinleştirme
        self.setAcceptDrops(True)

        # Silinecek Dosyalar
        self.file_paths = []

    def create_menu_bar(self):
        menubar = self.menuBar()
        language_menu = menubar.addMenu('Language')
        
        for lang in ['Turkish', 'English']:
            action = QAction(lang, self)
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))
            language_menu.addAction(action)

    def show_about_dialog(self, event=None):
        about_dialog = AboutDialog(self.translation)
        about_dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        if self.file_paths:
            self.drag_drop_label.setText(f"Seçilen: {', '.join(self.file_paths)}")
            self.delete_files()

    def delete_files(self):
        self.progress_bar.setValue(0)
        self.current_file_label.setText(self.translation['processing_start'])

        passes = {
            self.translation['security_levels'][0]: 1,
            self.translation['security_levels'][1]: 3,
            self.translation['security_levels'][2]: 7,
            self.translation['security_levels'][3]: 35
        }.get(self.security_combo.currentText(), 1)

        self.delete_thread = DeleteFilesThread(self.file_paths, passes, self.translation)
        self.delete_thread.progress_signal.connect(self.update_progress)
        self.delete_thread.complete_signal.connect(self.on_delete_complete)
        self.delete_thread.current_file_signal.connect(self.update_current_file)
        self.delete_thread.start()

    def update_current_file(self, file_name):
        """Güncel dosya ismini günceller"""
        self.current_file_label.setText(file_name)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_delete_complete(self, message):
        QMessageBox.information(self, "Tamamlandı", message)
        
        # Progress bar'ı sıfırlamak için timer kullanıyoruz
        QTimer.singleShot(2000, self.reset_progress_bar)

    def reset_progress_bar(self):
        """Progress bar'ı sıfırlayan metod"""
        self.progress_bar.setValue(0)
        self.current_file_label.setText("Hazır")
        self.drag_drop_label.setText("Dosya veya klasör sürükleyin ya da seçmek için herhangi bir yere tıklayın.")

    def mousePressEvent(self, event):
        """Form üzerinde herhangi bir yere tıklanınca dosya seçme diyalogu açılır."""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Dosya Seç", "", "Tüm Dosyalar (*)")
        if file_paths:
            self.file_paths = file_paths
            self.drag_drop_label.setText(f"Seçilen: {', '.join(file_paths)}")
            self.delete_files()

# Uygulama Başlatma
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if ICON_PATH:
        app.setWindowIcon(QIcon(ICON_PATH))
    window = SecureDeleteApp()
    window.show()
    sys.exit(app.exec_())