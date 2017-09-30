

define(function () {
  var socket;

  return {
      init: function(onmessage) {

        socket = new WebSocket("ws://localhost:3001/");

        socket.onopen = function (event) {
          socket.send(JSON.stringify({payload:"Here's some text that the server is urgently awaiting!"}));
        };

        socket.onmessage = onmessage
      }
  };
});
