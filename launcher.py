import sys
import threading
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


def resource_path(relative_path: str) -> Path:
    """
    Devuelve la ruta correcta tanto en desarrollo como dentro de PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent / relative_path


def open_browser():
    webbrowser.open("http://localhost:8501")


def main():
    app_path = resource_path("app.py")

    threading.Timer(3.0, open_browser).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
        "--server.port=8501",
    ]

    stcli.main()


if __name__ == "__main__":
    main()