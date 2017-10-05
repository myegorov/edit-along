// Client config
// prod ip comes from `ip addr`
var Conf = (function() {
  var host = {
    'dev' : '0.0.0.0',
    'prod': '0.0.0.0'
  };
  var port = {
    'dev' : 1070,
    'prod': 1070
  };

  return {
    host: host,
    port: port
  };
})();
