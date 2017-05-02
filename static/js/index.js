window.onload = function() {

  // test websockets
  // for Docker instance on domino.cs.rit.edu, use:
  // let sock = new WebSocket("ws://129.21.37.42:1070/websocket");
  let sock = new WebSocket("ws://localhost:1070/websocket");

  let textarea = document.getElementById('textarea');
  textarea.focus();



  // test working with cursors
  function getCaretCharacterOffsetWithin(element) {
    var caretOffset = 0;
    if (typeof window.getSelection != "undefined") {
      var range = window.getSelection().getRangeAt(0);
      var preCaretRange = range.cloneRange();
      preCaretRange.selectNodeContents(element);
      preCaretRange.setEnd(range.endContainer, range.endOffset);
      caretOffset = preCaretRange.toString().length;
    }
    return caretOffset;
  };

  function setCaretCharacterOffsetWithin(element, ix) {
    element.focus();
    var range = document.createRange();
    var sel = window.getSelection();
    var relIx = 0;
    var nodeIx = 0;
    var found = false;
    var ln = 0;
    // alert(element.innerHTML);
    for (var i = 0; i < element.childNodes.length; i++) {
      // alert(element.childNodes[i].nodeType);
      if (element.childNodes[i].nodeType == 3) {
        ln = element.childNodes[i].length;
      } else {
        ln = element.childNodes[i].innerText.length;
      }
      if (ix >= ln) {
        ix -= ln;
      } else {
        nodeIx = i;
        relIx = ix;
        found = true;
        break;
      }
    }
    if (found) {
      // alert("found loc at node " + nodeIx + " relIx " + relIx);
      if (element.childNodes[nodeIx].nodeType == 3) {
        range.setStart(element.childNodes[nodeIx], relIx);
        range.setEnd(element.childNodes[nodeIx], relIx+1);
      } else {
        range.setStart(element.childNodes[nodeIx].firstChild, relIx);
        range.setEnd(element.childNodes[nodeIx].firstChild, relIx+1);
      }
      range.collapse(true);
      sel.removeAllRanges();
      sel.addRange(range);
    }
  };


  // test firing events on changes
  let observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      sock.send(textarea.innerText);

      sock.onmessage = function(evt) {
        console.log(evt.data);

        console.log("selection (cursor??): " + 
                    JSON.stringify(getCaretCharacterOffsetWithin(textarea)));

        // now try resetting cursor to some arbitrary number
        if (getCaretCharacterOffsetWithin(textarea) > 20) {
          setCaretCharacterOffsetWithin(textarea, 8);
        }
      };

    });
  });

  let observerOptions = {
    subtree: true,
    characterData: true
  };

  observer.observe(textarea, observerOptions);


}
