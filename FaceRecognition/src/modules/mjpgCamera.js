var MjpegCamera = require('mjpeg-camera');
var util = require('util');
var Stream = require('stream');

/**
 *  @param {Object} options
 *    @param {Function=} options.transform
 *    @param {String=} options.ext
 *    @param {Boolean=} options.onData
 *    @param {Object=} options.context
 */

function StreamPipe(options) {
  options = options || {};

  this.transform = options.transform || function(data) { return data; };

  this.writable = true;
  this.context = options.context;
  this.filter = options.filter || function() { return true; };

  this.onData = options.onData;
}
util.inherits(StreamPipe, Stream);

StreamPipe.prototype.write = function(data) {

  // If the data doesn't pass the filter, return
  if (!this.filter(data)) return;
  // Transform the data before write
  var transformedData = this.transform.call(this.context, data);
  // Write data
  if (this.onData != null && this.onData != undefined)
  {
    this.onData.call(this.context,transformedData);
  }
};


StreamPipe.prototype.end = function(data) {
  this.write(data);
  this.writable = false;
};

StreamPipe.prototype.destroy = function() {
  this.writable = false;
};

var mjpgCamera = function () {
  let module = this;
  let streamPipe;
  let camera;
  //let sendData = true;
  let isCameraOn = false;
  let buffer;
  let streamCallback;
  let interval = 2;

  function init(config) {
    console.log(config);
    streamCallback = config.streamCallback;
    interval = config.interval;

    if (streamPipe == null){
      console.log("mjpg-consumer: create streampipe: "+config.uri);
      streamPipe = new StreamPipe({
        transform: function(frame) {
          return frame.data;
        },
        onData: saveFrame
      });
    }

    if (camera == null){
      // Create an MjpegCamera instance
      camera = new MjpegCamera({
        url: config.uri,
        motion: false
      });

    }

  }

  let timer;
      function setupStreamInterval() {
          console.log("mjpg-consumer: output interval (milliseconds): "+interval * 1000);
          clearInterval(timer);
          if (interval)
            timer = setInterval(sendBuffer, interval * 1000);
      }


  function start() {
    console.log("start camera")
    startCamera();
      setupStreamInterval();
    camera.pipe(streamPipe);
    //sendData = true;
  }

  function stop() {
    console.log("stop camera")
    stopCamera();
    clearInterval(timer);
  }

  function saveFrame(data){
    buffer = data;
    //streamCallback(data);
  }

  function sendBuffer() {
    streamCallback(buffer);
  }

  var startCamera = function(){
    if (isCameraOn == true)
      return;

    isCameraOn = true;
    camera.start();
  }

  var stopCamera = function(){
    camera.stop();
    clearInterval(timer);
    isCameraOn = false;
  }

  return {
    init,
    start,
    stop
  }
}();

module.exports = mjpgCamera;
