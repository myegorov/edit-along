// Client config
var Conf = (function() {
  var host = {
    'dev' : '127.0.0.1',
    'prod': '172.17.0.2'
  };
  var port = {
    'dev' : 8080,
    'prod': 1070
  };

  return {
    host: host,
    port: port
  };
})();
