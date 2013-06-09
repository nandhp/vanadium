Vanadium - A replacement for Google Chrome's broken "-remote" feature
=====================================================================

When I click on a link in another application, it's supposed to open in one of my existing browser windows.
But Google Chrome has a bug (on Linux), where it sometimes starts a new copy.
This is annoying, because it causes lots of problems next time I restart Chrome.
This project is a replacement for that feature.

Although the primary goal of the project is to  work around Chrome's broken "-remote" feature (by reimplementing it), the concept could be extended to add new features:

* Open links in a browser running on another computer
* Customize the behavior, e.g. open some links in Chrome and others in Firefox
* Adjust the browser's handling, e.g. opening the links in a new window instead of a new tab or opening them all in a dedicated window, rather than the most recently used window.

Don't expect too much, since it's just something I threw together in an evening.
Although even without trying it's noticably faster than the Chrome "-remote" feature.

Usage
-----

Vanadium is only tested on Linux.

First, run the Vanadium daemon:

    ./vanadium.py --daemon

Then load the extension in your browser (currently only Chrome is supported):

1. Go to Menu > Tools > Extensions
2. Check the box for Developer mode
3. Click Load Unpacked Extension and choose Vanadium''s `crx` subdirectory

Now, try opening a page:

    ./vanadium.py http://www.youtube.com/watch?v=oHg5SJYRHA0

The client, `vanadium.py`, could be set as your system's default web browser.

Known issues
------------

* Vanadium will not open the link if communication with the browser fails (e.g. if the browser is not running or has not loaded the extension)
* Vanadium does not convert relative pathnames to file: URLs
* No security is implemented

License
-------

    Vanadium - A replacement for Google Chrome's broken "-remote" feature
    Copyright (C) 2013 nandhp <nandhp@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

