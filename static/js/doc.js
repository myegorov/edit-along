/* Client Text & Client Shadow, stored in memory */
var Tabula = (function() {
  // Client Text
  var text = {
    'str': '',
    'updated': false // MutationObserver will update the flag on keystrokes
  };

  var shadow = {
    'str': '',       // contents of document
    'clock': [-1,-1] // initialize vector clock: <CLIENT_CLOCK, SERVER_CLOCK>
  };

  return {
    text:text,
    shadow:shadow
  };
})();
