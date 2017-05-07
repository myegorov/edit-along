var Client = (function () {

  var conf = Conf;

  var awaitResponse = false; // is client waiting on server to respond?

  var client_id = null; // to be set by Server

  /* parse client's URL */
  var parseURI = function() {
    let hostname = window.location.hostname,
        port = window.location.port,
        pathname = window.location.pathname;
    return { // note any one can be empty string
      hostname: hostname,
      port: port,
      pathname: pathname
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
    // console.log("conf: " + JSON.stringify(conf));
    var socket_url = 'ws://'+ conf.host[env] + ':' + conf.port[env] + '/websocket/' + doc;
    return socket_url;
  };


  return {
    parseURI: parseURI,
    lookupEnv: lookupEnv,
    sock: sock,
    client_id: client_id
  };
})();
