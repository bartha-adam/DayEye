var WebSocket = require('ws')
var WebSocketServer = WebSocket.Server;

var websocketServer = function(){
  var wss;
  var socket;

  var init = function(config){
    wss = new WebSocketServer({ port: config.websocket });
  }

  var onMessage = function(callback){
    wss.on('connection', function connection(ws) {
      socket = ws;
      ws.on('message', function incoming(message) {

        callback(message);

      });

    //  ws.send('something');
    });
  }

  function broadcast(data) {
    wss.clients.forEach(function each(client) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  };

  var send = function(data){
    if (socket == undefined)
      return;
    try {
      //console.log(socket.clients)
        //socket.send(data);
      broadcast(data);
    } catch (e) {
      console.log(e);
    } finally {

    }
  }

  return {
    init: init,
    onMessage: onMessage,
    send: send
  }
}();

module.exports = websocketServer;
