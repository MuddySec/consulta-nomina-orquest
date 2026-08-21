import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


PORT = 8501
URL = f"http://localhost:{PORT}"


def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent / relative_path


def log_error(text: str):
    try:
        desktop = Path.home() / "Desktop"
        log_path = desktop / "ConsultaNominaOrquest_error.log"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(text)
            f.write("\n\n")
    except Exception:
        pass


def is_port_open(host: str = "127.0.0.1", port: int = PORT) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def open_browser_when_ready():
    for _ in range(30):
        if is_port_open():
            webbrowser.open(URL)
            return
        time.sleep(1)

    log_error(
        f"No se pudo abrir {URL}. "
        "Streamlit no respondió después de 30 segundos."
    )
    webbrowser.open(URL)


def main():
    try:
        app_path = resource_path("app.py")

        threading.Thread(
            target=open_browser_when_ready,
            daemon=True,
        ).start()

        sys.argv = [
            "streamlit",
            "run",
            str(app_path),
            "--server.headless=true",
            f"--server.port={PORT}",
            "--server.address=127.0.0.1",
            "--browser.gatherUsageStats=false",
        ]

        stcli.main()

    except Exception:
        log_error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
