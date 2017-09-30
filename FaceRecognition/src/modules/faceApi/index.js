const oxford = require('project-oxford');


let faceApi = function (config) {
  let module = this;
  let socketCallback;
  let apiClient;
  let currentFrame;
  let isTraining = false;
  let isSendingFrames = false;
  let trainingTimer;
  let sendFramesTimer;
  let currentGroupId;
  let currentPersonId;
  let trainingFrameCount = 0;

  let registration;
  let training;

  module.config = config;

  init();

  function init() {
    apiClient = new oxford.Client(module.config.faceApiKey);

    group = require('./group')(apiClient);
    training = require('./training')(apiClient);
  }

  function onMjpgStream(frame) {
    //console.log(frame);
    currentFrame = frame;


  }

  function createGroup(groupName) {
    group.createGroup(groupName);
  }

  function register(personGroup, email) {
    currentGroupId = personGroup;
    if (isTraining || isSendingFrames)
      return;
    //try get person. if not exists, register
    apiClient.face.person.get(personGroup, email)
      .then(function(response) {
        console.log("register.get response")
        console.log(response);
      }, function (reject) {
        //person not found
        console.log("register.get reject")
        console.log(reject);

        if (reject.code == 'PersonNotFound') {
          console.log('Register new person')
          console.log(personGroup)
          console.log(email)
          apiClient.face.person.create(personGroup, email)
            .then(function(response) {
              console.log("register.create response")
              console.log(response)
              if (response.personId) {
                currentPersonId = response.personId;
                startSendingFrames(response.personId, email)
              }
            }, function (reject) {
              console.log("register.create reject")
              console.log(reject)
            });
        }
      });
  }

  function startSendingFrames(personId, email) {
    trainingFrameCount = 0;
    isSendingFrames = true;
    sendFramesTimer = setInterval(sendFrames, 2000)
    console.log("start sending frames for "+email);

  }

  function startTraining() {
    console.log("start training for "+currentGroupId+" person: "+currentPersonId);
    isTraining = true;

    apiClient.face.personGroup.trainingStart(currentGroupId)
      .then(function (response) {
        console.log("training start response")
        console.log(response)
      },
      function (reject) {
        console.log("training start reject")
        console.log(reject)
      });

    trainingProcess = setInterval(checkTrainStatus, 3000);
  }

  function checkTrainStatus() {
    console.log("check train status")
    apiClient.face.personGroup.trainingStatus(currentGroupId)
      .then(function (response) {
        console.log(response)
        if (response.status == 'succeeded')
          clearInterval(trainingProcess)
      },
      function (reject) {
        console.log(reject)
      });
  }

  function stopTraining() {
    clearInterval(trainingProcess)
    isTraining = false;

  }

  function sendFrames() {
    console.log("send frame");
    if (trainingFrameCount >= 5) {
      trainingFrameCount = 0;
      isSendingFrames = false;
      console.log("stop sending frames. Start training group")
      clearInterval(sendFramesTimer);

      startTraining();

      return;

    }
    else {
      trainingFrameCount++;
      detect().then(function (response) {
        if (response[0].faceRectangle) {
          addFace(currentGroupId, currentPersonId, currentFrame, response[0].faceRectangle);
        }
      },
      function (reject) {
        console.log("face detect reject")
        console.log(reject);
      });
    }
  }

  function isTrainingGroup() {
    return isTraining;
  }

  function addFace(groupId, personId, frame, targetFace) {

    apiClient.face.person.addFace(groupId, personId, {
      data: frame,
      targetFace: targetFace
    }).then(function (response) {
      console.log("add face response")
      console.log(response)
      trainingFrameCount++;
    },
    function (reject) {
      console.log("add face reject")
      console.log(reject)
    })
  }

  function detect() {
    return apiClient.face.detect({
      data: currentFrame,
      analyzesAge: true,
      analyzesGender: true,
      analyzesEmotion: true,
      returnFaceId: true
    });
  }

  function getPersonInfo(groupId, personId) {
    console.log(personId)
    return apiClient.face.person.get(groupId, personId);
  }

  function logObject(object) {
    return JSON.stringify(object);
  }

  function deleteGroup(groupName) {
    group.deleteGroup(groupName);
  }

  return {
    createGroup,
    onMjpgStream,
    register,
    isTrainingGroup,
    getPersonInfo,
    deleteGroup
  }
};

module.exports = faceApi;
