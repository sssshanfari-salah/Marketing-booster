import os
import sys
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SOURCE_DIR = APP_DIR / "python code"
DIST_DIR = APP_DIR / "dist"
BUILD_DIR = APP_DIR / "build"
SPEC_FILE = APP_DIR / "marketing_booster.spec"
DESKTOP_DIR = Path.home() / "Desktop"
TARGET_EXE = DIST_DIR / "marketing_booster" / "marketing_booster.exe"
TARGET_ICON = SOURCE_DIR / "icon.ico"


def ensure_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
        return True
    except ModuleNotFoundError:
        return False


def ensure_pywin32():
    try:
        import win32com.client  # noqa: F401
        return True
    except ModuleNotFoundError:
        return False


def build_app():
    if not ensure_pyinstaller():
        print("PyInstaller is not installed. Installing it now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"]) 

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name",
        "marketing_booster",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(APP_DIR),
        str(SOURCE_DIR / "main.py"),
    ]

    if TARGET_ICON.exists():
        cmd[0:0] = []
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--windowed",
            "--name",
            "marketing_booster",
            "--icon",
            str(TARGET_ICON),
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(BUILD_DIR),
            "--specpath",
            str(APP_DIR),
            str(SOURCE_DIR / "main.py"),
        ]

    print("Building app...")
    subprocess.check_call(cmd, cwd=str(APP_DIR))

    return TARGET_EXE


def create_shortcut():
    if not TARGET_EXE.exists():
        print("Executable not found. Build the app first.")
        return None

    if not ensure_pywin32():
        print("pywin32 is required to create the desktop shortcut. Install it with:")
        print("python -m pip install pywin32")
        return None

    desktop_link = DESKTOP_DIR / "Marketing Booster.lnk"
    shell = __import__("win32com.client").Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(desktop_link))
    shortcut.Targetpath = str(TARGET_EXE)
    shortcut.WorkingDirectory = str(TARGET_EXE.parent)
    shortcut.IconLocation = str(TARGET_EXE)
    shortcut.save()

    print(f"Shortcut created: {desktop_link}")
    return desktop_link


if __name__ == "__main__":
    if os.name != "nt":
        raise SystemExit("This packaging script is for Windows only.")

    exe = build_app()
    print(f"Built: {exe}")
    create_shortcut()
