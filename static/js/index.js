window.onload = function() {
  var SYNC_INTERVAL = 1000; // diff every 1 sec



  var dmp_exact = new diff_match_patch(0.0);
  var dmp_fuzzy = new diff_match_patch(0.4);
  var tab = Tabula;
  var client = Client;

  console.log('socket url: ' + client.sock());
  var sock = new WebSocket(client.sock());

  var textarea = document.getElementById('textarea');
  textarea.focus();

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
      sock.send(outgoing_queue.shift());

      sock.onmessage = function(evt) {
        patchClient(evt);
      }
    }
  }



  function snapshot() {
    /* check for any changes to Client Text & reset */
    if (! tab.text.updated) return;
    tab.text.updated = false;
    tab.text.str = textarea.innerText;

    /* diff Client Text (new) against Client Shadow (old) */
    var delta = dmp_exact.diff_main(tab.shadow.str, tab.text.str, false);
    var patch_txt = dmp_exact.patch_toText(
                        dmp_exact.patch_make(
                          tab.shadow.str, delta));

    /* compose message to server */
    var msg_to_server = {'clock': tab.shadow.clock,
                         'edits': patch_txt,
                         'client_id':client.client_id};

    /* snapshot Client Text to Client Shadow */
    tab.shadow.clock[0] += 1;
    tab.shadow.str = tab.text.str;

    /* yield control to mailman -> receive response & apply patch */
    outgoing_queue.push(JSON.stringify(msg_to_server));
  }
  var intervalHandle = setInterval(snapshot, SYNC_INTERVAL);


  function patchClient(evt) {
    // console.log(evt.data);

    /* decipher JSON message */
    var msg = JSON.parse(evt.data);

    /* assert that clock matches Client Shadow */
    if (JSON.stringify(msg.clock) != JSON.stringify(tab.shadow.clock)) {
      throw new Error('Clocks out of sync!');
    }

    /* apply exact patch to Client Shadow & update server's clock */
    tab.shadow.str = dmp_exact.patch_apply(
                          dmp_exact.patch_fromText(msg.edits), tab.shadow.str)[0]
    tab.shadow.clock[1] += 1;

    /* apply fuzzy patch to Client Text */
    var stale_client_text = tab.text.str; 
    tab.text.str = dmp_fuzzy.patch_apply(
                          dmp_fuzzy.patch_fromText(msg.edits), tab.text.str)[0]

    /* prettify edits in textarea  */
    //TODO: switch from patches to diffs as the currency of exchange
    //      since using diffs to display pretty html
    var delta = dmp_exact.diff_main(stale_client_text, tab.text.str, false);
    var html = dmp_fuzzy.diff_prettyHtml(delta)
    textarea.innerText = html;
  }

}






/////////////////////////////////////////
////////////////////////////////////////
/////////////////////////////////////////
////////////////////////////////////////

// window.onload = function() {

//   // test websockets
//   // for Docker instance on domino.cs.rit.edu, use:
//   // let sock = new WebSocket("ws://129.21.37.42:1070/websocket");
//   // let sock = new WebSocket("ws://localhost:8080/websocket");
//   let sock = new WebSocket("ws://localhost:8080/websocket/"+window.location.pathname);
//   console.log("window.location.pathname: " + window.location.pathname);

//   let textarea = document.getElementById('textarea');
//   textarea.focus();



//   // test working with cursors
//   function getCaretCharacterOffsetWithin(element) {
//     var caretOffset = 0;
//     if (typeof window.getSelection != "undefined") {
//       var range = window.getSelection().getRangeAt(0);
//       var preCaretRange = range.cloneRange();
//       preCaretRange.selectNodeContents(element);
//       preCaretRange.setEnd(range.endContainer, range.endOffset);
//       caretOffset = preCaretRange.toString().length;
//     }
//     return caretOffset;
//   };

//   function setCaretCharacterOffsetWithin(element, ix) {
//     element.focus();
//     var range = document.createRange();
//     var sel = window.getSelection();
//     var relIx = 0;
//     var nodeIx = 0;
//     var found = false;
//     var ln = 0;
//     // alert(element.innerHTML);
//     for (var i = 0; i < element.childNodes.length; i++) {
//       // alert(element.childNodes[i].nodeType);
//       if (element.childNodes[i].nodeType == 3) {
//         ln = element.childNodes[i].length;
//       } else {
//         ln = element.childNodes[i].innerText.length;
//       }
//       if (ix >= ln) {
//         ix -= ln;
//       } else {
//         nodeIx = i;
//         relIx = ix;
//         found = true;
//         break;
//       }
//     }
//     if (found) {
//       // alert("found loc at node " + nodeIx + " relIx " + relIx);
//       if (element.childNodes[nodeIx].nodeType == 3) {
//         range.setStart(element.childNodes[nodeIx], relIx);
//         range.setEnd(element.childNodes[nodeIx], relIx+1);
//       } else {
//         range.setStart(element.childNodes[nodeIx].firstChild, relIx);
//         range.setEnd(element.childNodes[nodeIx].firstChild, relIx+1);
//       }
//       range.collapse(true);
//       sel.removeAllRanges();
//       sel.addRange(range);
//     }
//   };


//   // test firing events on changes
//   let observer = new MutationObserver(function(mutations) {
//     mutations.forEach(function(mutation) {
//       sock.send(textarea.innerText);

//       sock.onmessage = function(evt) {
//         console.log(evt.data);

//         console.log("selection (cursor??): " + 
//                     JSON.stringify(getCaretCharacterOffsetWithin(textarea)));

//         // now try resetting cursor to some arbitrary number
//         if (getCaretCharacterOffsetWithin(textarea) > 20) {
//           setCaretCharacterOffsetWithin(textarea, 8);
//         }
//       };

//     });
//   });

//   let observerOptions = {
//     subtree: true,
//     characterData: true
//   };

//   observer.observe(textarea, observerOptions);


// }
