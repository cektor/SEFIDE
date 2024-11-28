from setuptools import setup

setup(
    name="sefide",
    version="1.0",
    packages=["sefide"],
    data_files=[("share/applications", ["sefide.desktop"])],
    entry_points={
        "console_scripts": [
            "sefide=sefide.main:main",
        ],
    },
)
