import os
import sys
import threading
import webbrowser
from pathlib import Path


PORT = 8501
URL = f"http://localhost:{PORT}"

# Muy importante: esto debe ir ANTES de importar streamlit
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"


from streamlit.web import cli as stcli  # noqa: E402


def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent / relative_path


def open_browser():
    webbrowser.open(URL)


def main():
    app_path = resource_path("app.py")

    threading.Timer(5.0, open_browser).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]

    stcli.main()


if __name__ == "__main__":
    main()
