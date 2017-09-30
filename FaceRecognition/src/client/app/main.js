define(function (require) {
    // Load any app-specific modules
    // with a relative require call,
    // like:
    var api = require('./api');
    var cameraViewModel = require('./computerVision')
    var socketClient = require('./socketClient')


    let mainVM = function () {
      let module = this;
      module.camera = new cameraViewModel.Camera();
      module.camera.init();
      module.faceApiResponse = ko.observable();
      module.email = ko.observable();
      module.registerFace = function() {
        if (module.email())
          api.registerFace({email: module.email()}, function (data) {
            console.log(data)
          })
      }
      module.uploadFace = function() {
        console.log("Start uploading frames to face api")
      }

      function onSocketMessage(event) {
        //console.log(event.data);

        let msg = JSON.parse(event.data);

        if (msg.sender == 'faceApi') {
          module.faceApiResponse(JSON.stringify(msg.payload))
        }
      }

      return {
        onSocketMessage
      };

    }

    socketClient.init(mainVM().onSocketMessage);


    ko.applyBindings(mainVM);
});
