define (function(require) {
  var api = require('./api');
  return {
    Camera: function() {
      let module = this;
      module.init = function () {
        api.getConfig(function(data) {
          data = JSON.parse(data)
          module.Uri(data.mjpgStreamUri);
          module.View('<img src="'+data.mjpgStreamUri+'" alt="Camera Stream" width="320" height="240"></img>');
          console.log(data);
        })
      },
      module.Uri = ko.observable("mjpg uri");
      module.View = ko.observable();
    }
  }
})
