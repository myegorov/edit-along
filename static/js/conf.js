// Client config
// prod ip comes from `ip addr`
var Conf = (function() {
  var host = {
    'dev' : '127.0.0.1',
    'prod': '129.21.37.42' // ip exposed by server on top of which Docker runs
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
