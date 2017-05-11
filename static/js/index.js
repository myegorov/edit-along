window.onload = function() {
  var SYNC_INTERVAL = 500; // diff every 1 sec?
  var CURSOR = '¶';

  var dmp_exact = new diff_match_patch(0.0);
  var dmp_fuzzy = new diff_match_patch(0.4);

  // TODO: is there any need for tab.text.str??? isn't textarea enough??
  var tab = Tabula;
  var client = Client;


  (function initializeClientText() {
    // wait to take snapshots until we've established connection with server
    client.awaitResponse = true;
    var sock = new WebSocket(client.sock());
    /* compose initial message to server */
    sock.onopen = function() {
      var msg_to_server = JSON.stringify(
        {'clock': tab.shadow.clock,
         'edits': '',
         'client_id':client.client_id,
         'init': true}); // signal we're not intending to overwrite Server Text

      sock.send(msg_to_server);

      /* update Client's clock */
      tab.shadow.clock[0] += 1;

      console.log('packet sent' + JSON.stringify(msg_to_server));

      sock.onmessage = function(evt) {
        console.log('got mesage: ' + evt.data);
        patchClient(evt);
        sock.close();
      };
    }
  })();

  var textarea = document.getElementById('textarea');
  textarea.focus();

  // TODO: no need for observer? if we're sending/querying for updates anyway
  // reset flag on keystrokes
  var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      tab.text.updated = true;
      // console.log(textarea.innerText);
    });
  });
  var observerOptions = {
    subtree: true,
    characterData: true
  };
  observer.observe(textarea, observerOptions);


  var outgoing_queue = []; // message queue
  outgoing_queue.push = function() {
    Array.prototype.push.apply(this, arguments);
    mailman();
  };


  function mailman() {
    if (outgoing_queue.length > 0) {
      var sock = new WebSocket(client.sock());
      sock.onopen = function() {
        let packet = outgoing_queue.shift();
        console.log('sending packet...' + JSON.stringify(packet));
        sock.send(packet);

        sock.onmessage = function(evt) {
          console.log('got mesage: ' + evt.data);
          patchClient(evt);
          sock.close();
        };
      };
    }
  }



  function snapshot() {
    /* check for any changes to Client Text & reset */

    // TODO: check if this is needed?
    // check if server has responded to previous diff
    // hold off on synchronizing w/ server until certain that
    // connection has been established
    if (client.awaitResponse) return;
    // if (! tab.text.updated) return; // we're also interested in any server updates
    tab.text.updated = false;
    // tab.text.str = textarea.innerText;
    tab.text.str = textarea.value;

    /* diff Client Text (new) against Client Shadow (old) */
    var delta = dmp_exact.diff_main(tab.shadow.str, tab.text.str, false);
    var patch_txt = dmp_exact.patch_toText(
                        dmp_exact.patch_make(
                          tab.shadow.str, delta));

    // TODO: check if this is needed?
    var sync = (patch_txt === '') || false; // signal we're not intending to overwrite Server Text

    /* compose message to server */
    var msg_to_server = {'clock': tab.shadow.clock,
                         'edits': patch_txt,
                         'client_id':client.client_id,
                         'sync': sync};

    /* yield control to mailman -> receive response & apply patch */
    outgoing_queue.push(JSON.stringify(msg_to_server));

    /* snapshot Client Text to Client Shadow */
    tab.shadow.clock[0] += 1;
    tab.shadow.str = tab.text.str;
    client.awaitResponse = true;
  }
  var intervalHandle = setInterval(snapshot, SYNC_INTERVAL);


  function patchClient(evt) {
    // console.log(evt.data);

    /* decipher JSON message */
    var msg = JSON.parse(evt.data);

    /* assert that clock matches Client Shadow */
    if (JSON.stringify(msg.clock) != JSON.stringify(tab.shadow.clock)) {
      console.log("message clock: " + msg.clock + "; shadow.clock: " + tab.shadow.clock);
      throw new Error('Clocks out of sync!');
    } else if (msg.edits === '') {
      // no changes on server
      // just update tab.shadow.clock
      client.client_id = msg.client_id;
      tab.shadow.clock[1] += 1;
    } else {
      /* apply exact patch to Client Shadow & update server's clock */
      // set client_id if not set
      client.client_id = msg.client_id;
      tab.shadow.str = dmp_exact.patch_apply(
                            dmp_exact.patch_fromText(msg.edits), tab.shadow.str)[0]
      console.log('applied exact patch to client shadow: ' + tab.shadow.str);
      tab.shadow.clock[1] += 1;

      /* apply fuzzy patch to Client Text */
      // get cursor position
      textarea.focus();
      var cursorPos = textarea.selectionStart;

      var textSnapshot = textarea.value;
      var textWithCursor = textSnapshot.slice(0,cursorPos) + CURSOR +
                            textSnapshot.slice(cursorPos);
      var updatedText = dmp_fuzzy.patch_apply(
                            dmp_fuzzy.patch_fromText(msg.edits), textWithCursor)[0]
      // now extract cursor char & reset cursor
      var newCursorPos = updatedText.indexOf(CURSOR);
      if (newCursorPos < 0) {
        newCursorPos = 0; // revert to start of text
      } else { // excise cursor
        updatedText = updatedText.slice(0,newCursorPos) + 
                                updatedText.slice(newCursorPos+1);
      }

      tab.text.str = updatedText;
      textarea.value= updatedText;

      // update cursor
      textarea.focus();
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }
    client.awaitResponse = false;
  }
}
