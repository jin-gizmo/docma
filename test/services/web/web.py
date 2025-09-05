"""
Hacked basic web server setup for testing.

This allows us to manipulate which methods are allowed and response headers
from the client side.

It only supports HEAD and GET.

The following query parameters are supported:

*   allow=METHOD[,...]
    Only allow the listed methods. Others will return 403. If not specified,
    the effect is the same as allow=HEAD,GET

*   header=key/value
    Set the response header to the specified value. If the value is empty, the
    header is deleted from the response. This parameter can be used multiple
    times to set multiple headers.

"""

import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from signal import SIGINT, SIGTERM, signal
from threading import Thread
from urllib.parse import parse_qs, urlparse


# ------------------------------------------------------------------------------
class CustomHandler(SimpleHTTPRequestHandler):
    """Custom web server for testing."""

    # --------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initialize request handler with buffers for query params and headers."""
        self._pending_headers = []
        self._query = {}
        super().__init__(*args, **kwargs)

    # --------------------------------------------------------------------------
    def send_head(self):
        """Handle GET/HEAD: enforce allow rules, parse query, serve file."""

        purl = urlparse(self.path)
        self._query = parse_qs(purl.query)
        self._pending_headers = []

        # Check if this is an allowed request method.
        if 'allow' in self._query:
            allowed = {m.strip().upper() for val in self._query['allow'] for m in val.split(',')}
            if self.command not in allowed:
                self.send_response(403)
                self.end_headers()
                if self.command == 'GET':
                    self.wfile.write(b'Forbidden')
                return None

        self.path = purl.path
        return super().send_head()

    # --------------------------------------------------------------------------
    def send_header(self, keyword, value):
        """Buffer headers instead of sending immediately."""

        self._pending_headers.append((keyword, value))

    # --------------------------------------------------------------------------
    def end_headers(self):
        """Apply header deletions/overrides, then flush headers."""

        header_params = self._query.get('header', [])

        # Compute deletions and additions
        delete_keys = set()
        additions = []
        for h in header_params:
            if '/' in h:
                k, v = h.split('/', 1)
                kl = k.strip()
                if not v:
                    delete_keys.add(kl.lower())
                else:
                    additions.append((kl, v))

        # Remove any requested headers
        self._pending_headers = [
            (k, v) for (k, v) in self._pending_headers if k.lower() not in delete_keys
        ]

        # Apply overrides/additions (last wins)
        for k_new, v_new in additions:
            self._pending_headers = [
                (k, v) for (k, v) in self._pending_headers if k.lower() != k_new.lower()
            ]
            self._pending_headers.append((k_new, v_new))

        # Flush headers using superclass
        for k, v in self._pending_headers:
            super().send_header(k, v)

        # Reset buffers
        self._pending_headers = []
        self._query = {}

        super().end_headers()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), CustomHandler)

    def run():
        """Run the web server in a separate thread for quicker shutdown."""
        server.serve_forever()
        server.serve_forever(poll_interval=0.1)

    thread = Thread(target=run)
    thread.start()

    # noinspection PyUnusedLocal
    def shutdown(sig, frame):
        """Handle shutdown signals."""
        print('Shutting down...')
        server.shutdown()
        server.server_close()
        sys.exit(0)

    signal(SIGTERM, shutdown)
    signal(SIGINT, shutdown)

    print('Serving test server on http://0.0.0.0:8080')
    thread.join()
