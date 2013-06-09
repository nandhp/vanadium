function reinit() {
    var eventd = new EventSource('http://localhost:8636/stream');
    eventd.addEventListener('openurl', function (e) {
        if ( e.data )
        chrome.tabs.create({'url': e.data})
    }, false);
    eventd.addEventListener('error', function (e) {
        if ( eventd.readyState == 2 ) {
            eventd.close();
            //reinit();
        }
    }, false);
}
reinit();
