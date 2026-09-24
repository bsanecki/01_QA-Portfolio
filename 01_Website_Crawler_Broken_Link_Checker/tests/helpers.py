"""Local HTTP test server + scan helpers used by the test-suite."""

import os
import sys
import threading
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scan_engine import ScanConfig, ScanEngine  # noqa: E402


def html(*body, head=""):
    return (
        "<html><head>" + head + "</head><body>" + "".join(body) + "</body></html>"
    ).encode()


def links(*paths):
    return "".join(f'<a href="{p}">{p}</a>' for p in paths)


class Site:
    """Threaded HTTP server. `routes` maps a path to either
    bytes/str (200 text/html) or a callable(handler) -> None that writes the
    response itself. Every request is recorded in `hits`."""

    def __init__(self, routes=None, delay=0.0):
        self.routes = dict(routes or {})
        self.delay = delay
        self.hits = Counter()          # (METHOD, path) -> count
        self.log = []                  # [(time, METHOD, path)]
        self.lock = threading.Lock()
        self.active = 0
        self.max_active = 0
        site = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def _serve(self, method):
                path = self.path
                with site.lock:
                    site.hits[(method, path)] += 1
                    site.log.append((time.monotonic(), method, path))
                    site.active += 1
                    site.max_active = max(site.max_active, site.active)
                try:
                    if site.delay:
                        time.sleep(site.delay)
                    route = site.routes.get(path.split("#")[0])
                    if route is None:
                        return self.reply(404, b"not found")
                    if callable(route):
                        return route(self, method)
                    if isinstance(route, str):
                        route = route.encode()
                    return self.reply(200, route)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                finally:
                    with site.lock:
                        site.active -= 1

            def reply(self, status, body=b"", ctype="text/html; charset=utf-8",
                      headers=None, send_body=True):
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                for key, value in (headers or {}).items():
                    self.send_header(key, value)
                self.end_headers()
                if send_body and self.command != "HEAD":
                    self.wfile.write(body)

            def do_GET(self):
                self._serve("GET")

            def do_HEAD(self):
                self._serve("HEAD")

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.httpd.daemon_threads = True
        self.port = self.httpd.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def url(self, path="/"):
        return self.base + path

    def count(self, path, method="GET"):
        return self.hits[(method, path)]

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def redirect(status, location):
    def handler(h, method):
        h.reply(status, b"", headers={"Location": location})
    return handler


def status_route(status, body=b"x", headers=None):
    def handler(h, method):
        h.reply(status, body, headers=headers)
    return handler


def run_scan(url, depth=5, timeout=90, **config):
    engine = ScanEngine(ScanConfig(start_url=url, max_depth=depth, **config))
    engine.start()
    assert engine.finished.wait(timeout), "scan did not finish in time"
    return engine


def by_url(engine):
    return {link.url: (link, result) for link, result in engine.results}


def categories(engine):
    return {url: result.category for url, (link, result) in by_url(engine).items()}
