import threading
import time
import webbrowser

import uvicorn

from eu4th.ui import webapp

HOST, PORT = "127.0.0.1", 8000


def _open_browser_delayed(host, port):
    time.sleep(2)
    webbrowser.open(f"{host}:{port}")


def serve():
    """Serve the web application."""
    threading.Thread(target=_open_browser_delayed, args=[HOST, PORT]).start()
    uvicorn.run(webapp, host=HOST, port=PORT)


if __name__ == "__main__":
    serve()
