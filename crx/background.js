function reinit() {
    var eventd = new EventSource('http://localhost:8636/stream');
    eventd.addEventListener('openurl', function (e) {
        if ( e.data )
            chrome.tabs.create({'url': e.data})
        else
            chrome.windows.create()
    }, false);
    eventd.addEventListener('error', function (e) {
        if ( eventd.readyState == 2 ) {
            eventd.close();
            //reinit();
        }
    }, false);
}
reinit();
