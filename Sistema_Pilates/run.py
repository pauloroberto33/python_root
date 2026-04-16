import socket
import threading
import webbrowser
import uvicorn


def find_open_port(start_port=8000, max_port=8100):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("Não foi possível encontrar uma porta livre entre 8000 e 8099.")


def open_browser(url):
    try:
        webbrowser.open(url)
    except Exception:
        pass


if __name__ == "__main__":
    port = find_open_port()
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.0, lambda: open_browser(url)).start()
    uvicorn.run("main:app", host="127.0.0.1", port=port, log_level="info")
