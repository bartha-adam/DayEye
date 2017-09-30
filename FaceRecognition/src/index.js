function socketCallback(data) {
  console.log("socket callback")
  console.log(data);
  websocketServer.send(JSON.stringify(data));
}


// websocket server
var websocketServer = require('./modules/websocketServer');

// express
const express = require('express')
const app = express()
const bodyParser= require('body-parser')

// load config
const config = require('./config.json')

// face Api
const faceApi = require('./modules/faceApi')(config);

// create Macadamian groupName
faceApi.createGroup('macadamian');



// configure express app
app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded
app.use(express.static('client'))



// configure websocket server
websocketServer.init({websocket:config.websocket});
websocketServer.onMessage(function(message){
  try {
    var msg = JSON.parse(message);
    console.log(msg);
    if (msg != undefined){
      if (msg.payload == undefined){
        websocketServer.send("Missing payload field")
      }
      else {

      }
    }
    else {
      websocketServer.send("Undefined message")
    }

  } catch (e) {
    console.log(e);
  } finally {

  }
});

app.get('/test', function (req, res){
  let obj = {
    test:"test value"
  }

  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(obj));
})
.get('/config', function(req, res) {
  res.send(JSON.stringify(config));
})
.get('/face/isTraining', function () {
  let isTraining = faceApi.isTrainingGroup();

  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({isTraining:isTraining}));
})
.get('/face/personInfo', function (req, res) {
  console.log(req.query.personId);
  faceApi.getPersonInfo('macadamian',req.query.personId)
    .then(function (response) {
      console.log('person info')
      console.log(response);

      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify(response));
    },
    function (reject) {
      console.log('reject person info')
      console.log(reject)
    });


})
.post('/face/register', function(req, res) {
  //let body = JSON.parse(req.body)
  if (faceApi.isTrainingGroup())
  {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({status:"isTraining"}));
    return;
  }
  faceApi.register('macadamian', req.body.email);

  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({status:"startedTraining"}));
})
.get('/group/delete', function(req, res) {
  const group = req.query.group;

  faceApi.deleteGroup(group);
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({status:"success"}));
})
.get('/group/create', function(req, res) {
  const group = req.query.group;

  faceApi.createGroup(group);
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({status:"success"}));
})


//Start server on specified port
app.listen(config.port, function () {
  console.log('Example app listening on port '+config.port)
})
