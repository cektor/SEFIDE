import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QFileDialog, QProgressBar,
    QWidget, QComboBox, QMessageBox, QDialog, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

# sefidelo.png ve uygulama ikonunun yolunu belirleme
def get_logo_path():
    if hasattr(sys, "_MEIPASS"):  # PyInstaller ile paketlenmişse
        return os.path.join(sys._MEIPASS, "sefidelo.png")
    elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/sefidelo.png"):
        return "/usr/share/icons/hicolor/48x48/apps/sefidelo.png"
    elif os.path.exists("sefidelo.png"):
        return "sefidelo.png"
    return None

def get_icon_path():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "sefidelo.png")
    elif os.path.exists("sefidelo.png"):
        return "sefidelo.png"
    return None

LOGO_PATH = get_logo_path()
ICON_PATH = get_icon_path()

# Güvenli silme algoritması
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

# "Hakkında" penceresi
class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hakkında")
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: #1F1F1F; color: white;")

        about_layout = QVBoxLayout()
        about_label = QLabel("\n\n"
            "SEFIDE\n"
            "(SEcure FIle DEstructor)\n\n"
            " SEFIDE, dosya ve klasörlerinizi güvenli bir şekilde kalıcı olarak yok etmeniz için tasarlanmış güçlü bir araçtır. Günümüzde, hassas bilgilerin ve dosyaların yanlış ellere geçmesi ciddi güvenlik sorunlarına yol açabilir. Bu uygulama, dijital güvenliğinizi sağlamak için geliştirilmiştir.\n\n"
            " Geliştirici: ALG Yazılım Inc. | www.algyzilim.com | info@algyazilim.com\n\n"
            " Fatih ÖNDER (CekToR) | wwww.fatihonder.org.tr | fatih@algyazilim.com\n\n"
            " EnCo Tüm Hakları Saklıdır. 2024 ALG Software Inc\n\n"
            " \n\n"
            " ALG Yazılım Pardus'a Göç'ü Destekler.")
        about_label.setWordWrap(True)  # Metnin taşmaması için kelime sarma etkinleştirildi
        about_label.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_label)

        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.close)
        about_layout.addWidget(close_button)

        self.setLayout(about_layout)

# Ana uygulama
class SecureDeleteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ SEFIDE ✨")
        self.setFixedSize(320, 450)
        self.setStyleSheet("background-color: #1F1F1F; color: white;")

        # Uygulama ikonunu ayarlama
        if ICON_PATH:
            self.setWindowIcon(QIcon(ICON_PATH))

        # Ana widget ve layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # "Hakkında" butonu
        about_button = QPushButton("...")
        about_button.clicked.connect(self.show_about_dialog)
        main_layout.addWidget(about_button)

        # "SEFIDE" başlık
        sefide_label = QLabel("SEFIDE")
        sefide_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0a500;")
        sefide_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(sefide_label)

        # Açıklama etiketi
        description_label = QLabel("SEcure FIle DEstructor")
        description_label.setWordWrap(True)  # Kelime sarma etkinleştirildi
        description_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0a500;")
        description_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description_label)

        # Logo
        logo_label = QLabel()
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            logo_pixmap = QPixmap(LOGO_PATH)
            logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        else:
            logo_label.setText("Logo yüklenemedi")
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        # Güvenlik seviyesi
        self.security_label = QLabel("Güvenlik Seviyesi:")
        self.security_combo = QComboBox()
        self.security_combo.addItems(["Hızlı (1 Geçiş)", "Orta (3 Geçiş)", "Yüksek (7 Geçiş)", "Gutmann (35 Geçiş)"])
        main_layout.addWidget(self.security_label)
        main_layout.addWidget(self.security_combo)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Mesaj alanı
        self.drag_drop_label = QLabel("Dosya veya klasör sürükleyin ya da seçmek için herhangi bir yere tıklayın.")
        self.drag_drop_label.setWordWrap(True)  # Kelime sarma etkinleştirildi
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.drag_drop_label)

        # Sürükle bırak etkinleştirme
        self.setAcceptDrops(True)

        # Silinecek dosyalar
        self.file_paths = []

    def show_about_dialog(self):
        """Hakkında penceresini açar."""
        about_dialog = AboutDialog()
        about_dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        if self.file_paths:
            self.drag_drop_label.setText(f"Seçilen: {self.file_paths[0]}")
            self.delete_files()

    def delete_files(self):
        passes = {
            "Hızlı (1 Geçiş)": 1,
            "Orta (3 Geçiş)": 3,
            "Yüksek (7 Geçiş)": 7,
            "Gutmann (35 Geçiş)": 35
        }.get(self.security_combo.currentText(), 1)

        total_files = len(self.file_paths)
        for index, file in enumerate(self.file_paths):
            self.progress_bar.setValue(int((index + 1) / total_files * 100))
            QApplication.processEvents()

            if not overwrite_file(file, passes):
                QMessageBox.critical(self, "Hata", f"{file} dosyası yok edilemedi!")
            else:
                print(f"{file} dosyası başarıyla yok edildi!")

        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Tamamlandı", "Dosya(lar) başarıyla yok edildi!")

    def mousePressEvent(self, event):
        """Form üzerinde herhangi bir yere tıklanınca dosya seçme diyalogu açılır."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Tüm Dosyalar (*)")
        if file_path:
            self.file_paths = [file_path]
            self.drag_drop_label.setText(f"Seçilen: {file_path}")
            self.delete_files()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SecureDeleteApp()
    window.show()
    sys.exit(app.exec())