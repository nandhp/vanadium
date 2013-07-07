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
import subprocess

BROWSER_COMMAND = '/usr/bin/google-chrome'

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
        if self.path in ('/open', '/open-wait'):
            # Verify a consumer is available, waiting if directed
            ok = False
            iters = 20 if 'wait' in self.path else 1
            for i in range(iters):
                with self.server.readylock:
                    if self.server.ready > 0:
                        ok = True
                if ok:
                    break
                elif i < iters-1:
                    time.sleep(1)
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

class BrowserError(Exception):
    pass

def error_prompt(message):
    import gtk
    dlg = gtk.Dialog(title='Web Browser Error')
    # Buttons
    #runbrowser = gtk.Button('Start Web Browser')
    #dlg.action_area.pack_start(runbrowser)
    #dlg.action_area.pack_start(gtk.Alignment(), expand=True, fill=True)
    dlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    dlg.add_button('_Retry All', gtk.RESPONSE_OK)
    dlg.set_default_response(gtk.RESPONSE_OK)
    # Dialog contents
    box = gtk.HBox()
    icon = gtk.Image()
    icon.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
    iconalign = gtk.Alignment(0.5, 0, 0, 0)
    iconalign.add(icon)
    iconalign.set_padding(0, 0, 12, 0)
    label = gtk.Label(("<big><b>Could not open all pages</b></big>\n\n" +
                       "An error occurred while opening some pages:\n%s") %
                      message)
    label.set_use_markup(True)
    labelalign = gtk.Alignment(0, 0, 0, 0)
    labelalign.set_padding(0, 12, 0, 0)
    labelalign.add(label)
    checkbox = gtk.CheckButton('_Start web browser before retrying')
    contentbox = gtk.VBox()
    contentbox.pack_start(labelalign, True, True)
    contentbox.pack_start(checkbox, False, False)
    box.pack_start(iconalign, False, False)
    box.pack_start(contentbox, True, True, padding=12)
    dlg.vbox.pack_start(box, padding=12)
    dlg.show_all()
    reply = dlg.run()
    cbstatus = checkbox.get_active()
    dlg.destroy()
    while gtk.events_pending():
        gtk.main_iteration(block=False)
    if reply == gtk.RESPONSE_OK and cbstatus:
        subprocess.Popen(BROWSER_COMMAND)
        return 1
    return 0 if reply == gtk.RESPONSE_OK else None

def open_url(url, do_wait=0):
    # FIXME: Support relative filenames
    obj = urlopen('http://127.0.0.1:%d/%s' %
                  (PORT, 'open-wait' if do_wait else 'open'), url)
    code = obj.getcode()
    if code == 200:
        return
    elif code == 503:
        raise BrowserError, '503: Browser not running'
    elif code is None:
        raise BrowserError, 'Daemon not running?'
    else:
        raise BrowserError, 'Got strange response code: %d' % code

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
    else:
        do_wait = 0
        while True:
            try:
                if len(argv) > 1:
                    # Open windows
                    for i in argv[1:]:
                        open_url(i, do_wait)
                else:
                    open_url('', do_wait)
                break
            except BrowserError, exception:
                do_wait = error_prompt(exception[0]+".")
                if do_wait is None:
                    break

if __name__ == '__main__':
    main(sys.argv)
