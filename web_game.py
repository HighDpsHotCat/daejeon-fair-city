from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.request import urlopen
import webbrowser


ROOT = Path(__file__).resolve().parent / "Web"
HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}/"


class GameFiles(SimpleHTTPRequestHandler):
    server_version = "DaejeonGame/1"

    def guess_type(self, path):
        if path.endswith(".unityweb"):
            path = path.removesuffix(".unityweb")
        return super().guess_type(path)

    def end_headers(self):
        # This build uses gzip for Unity's .unityweb payloads.
        if self.path.split("?", 1)[0].endswith(".unityweb") and getattr(self, "encoded", False):
            self.send_header("Content-Encoding", "gzip")
        super().end_headers()

    def send_head(self):
        self.encoded = Path(self.translate_path(self.path)).is_file()
        return super().send_head()


def main():
    if not (ROOT / "index.html").is_file():
        sys.exit("Web 폴더에서 게임 파일을 찾을 수 없습니다.")
    open_browser = "--no-browser" not in sys.argv
    try:
        server = ThreadingHTTPServer((HOST, PORT), partial(GameFiles, directory=str(ROOT)))
    except OSError as error:
        try:
            with urlopen(URL, timeout=2) as response:
                existing = response.headers.get("Server", "").startswith(GameFiles.server_version + " ")
        except OSError:
            existing = False
        if not existing:
            sys.exit(f"게임 서버를 시작할 수 없습니다. {error}")
        if open_browser:
            webbrowser.open(URL)
        return
    with server:
        print(f"공정도시 대전  {URL}\n이 창을 닫으면 게임 서버가 종료됩니다.", flush=True)
        if open_browser:
            webbrowser.open(URL)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
