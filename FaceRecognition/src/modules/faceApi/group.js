let registration = function(apiClient) {
  let module = this;
  module.apiClient = apiClient;

  function createGroup(groupName) {
    if (isExistingGroup(groupName)){
      console.log("group exists")
      return;
    }

    apiClient.face.personGroup
      .create(groupName, groupName)
      .then(function (response) {
        console.log("create group success")
        console.log(response)
      },
      function (reject) {
        console.log("create group failed")
        console.log(reject)
      });
  }

  function isExistingGroup(groupName) {
    apiClient.face.personGroup.get(groupName)
      .then(function(response) {
        console.log(response)
        return true;
      }, function (reject) {
        console.log(reject)
        return false;
      });
  }

  function deleteGroup(groupName) {
    console.log("deleting group "+groupName);
    apiClient.face.personGroup.delete(groupName)
      .then(function(response) {
        console.log(response)
        return true;
      }, function (reject) {
        console.log(reject)
        return false;
      });
  }

  return {
    createGroup,
    deleteGroup
  }
};

module.exports = registration;
