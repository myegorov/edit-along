var Client = (function () {

  var conf = Conf;

  var client_id = null; // to be set by Server

  /* parse client's URL */
  var parseURI = function() {
    return { // note any one can be empty string
      hostname: window.location.hostname,
      port: window.location.port,
      pathname: window.location.pathname
    }
  };

  var lookupEnv = function() {
    var parsed = parseURI();
    if (parsed.port == conf.port.dev || 
       parsed.hostname == conf.host.dev || 
       parsed.hostname == 'localhost') {
      return 'dev';
    } else {
      return 'prod';
    }
  }

  var sock = function() {
    var env = lookupEnv();
    var parsed = parseURI();
    var parts = parsed.pathname.split('/')
    var doc = parsed.pathname.endsWith('/') ? parts[parts.length-2] : parts[parts.length-1]
    var socket_url = 'ws://'+ conf.host.env + ':' + conf.port.env + '/websocket/' + doc;
    // var socket = new WebSocket('ws://'+ conf.host.env + ':' + conf.port.env + '/websocket/' + doc);
    return socket_url;
  };


  return {
    parseURI: parseURI,
    lookupEnv: lookupEnv,
    sock: sock,
    client_id: client_id
  };
})();
