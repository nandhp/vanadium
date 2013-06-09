#!/usr/bin/env python

"""Vanadium - A replacement for Google Chrome's broken "-remote" feature."""

PORT = 8636 # VNDM

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import time
from threading import Lock
from Queue import Queue, Empty
import sys
from urllib import urlopen

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    ready = False
    events = Queue()
    readylock = Lock()
    # FIXME: Need some kind of security

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream':
            # Communicate with a browser using Server-Sent Events
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.end_headers()
            # Clear queue of waiting items
            try:
                while True:
                    self.server.events.get(False)
            except Empty:
                pass
            # Set ready flag
            with self.server.readylock:
                self.server.ready += 1
            # Process queue
            try:
                while True:
                    try:
                        e = self.server.events.get(timeout=5)
                        if e is None:
                            break
                    except Empty:
                        self.wfile.write(": still alive\r\n")
                    else:
                        self.wfile.write("event: openurl\r\ndata: %s\r\n\r\n" % e)
            finally:
                # Clear ready flag
                with self.server.readylock:
                    assert(self.server.ready > 0)
                    self.server.ready -= 1
        else:
            self.send_error(404)

    def do_POST(self):
        # Read postdata
        try:
            datalen = int(self.headers.getheader('Content-Length'))
            data = self.rfile.read(datalen)
        except:
            self.send_error(400)
            return
        if self.path == '/open':
            # Verify a consumer is available
            ok = True
            with self.server.readylock:
                if self.server.ready <= 0:
                    ok = False
            if ok:
                if '\r' in data or '\n' in data:
                    self.send_error(400)
                else:
                    self.server.events.put(data)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write("OK\n")
            else:
                self.send_error(503)
        else:
            self.send_error(404)

    def log_request(self, code='-', size='-'):
        if not code or code != 200:
            return BaseHTTPRequestHandler.log_request(self, code, size)
        pass


def open_url(url):
    # FIXME: Support relative filenames
    obj = urlopen('http://127.0.0.1:%d/open' % (PORT,), url)
    code = obj.getcode()
    if code == 200:
        return
    elif code == 503:
        raise Exception, '503: Browser not running'
    elif code is None:
        raise Exception, 'Daemon not running?'
    else:
        raise Exception, ('Got strange response code', code) 

def main(argv):
    # FIXME: Use real argument parsing
    if '--help' in argv or '-h' in argv:
        sys.stderr.write("Usage: %s --daemon\n       %s [url [...]]\n" %
                         (argv[0], argv[0]))
        sys.exit(1)
    elif '--daemon' in argv:
        httpd = ThreadedHTTPServer(("127.0.0.1", PORT), Handler)
        print "serving at port", PORT
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.events.put(None)
    elif len(argv) > 1:
        # Open windows
        for i in argv[1:]:
            open_url(i)
    else:
        open_url('')

if __name__ == '__main__':
    main(sys.argv)

