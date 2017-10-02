angular.module('starter.controllers', [])

.controller('DashCtrl', function($scope) {
  document.addEventListener('deviceready', deviceReady, false);

  function deviceReady() {
      //I get called when everything's ready for the plugin to be called!
      console.log('Device is ready!');
      // window.plugins.googleplus.trySilentLogin({'webClientId': '732334025518-c4n0e2knugu3oapjtvmmb6nvt4tfg7mb.apps.googleusercontent.com'});
      window.plugins.googleplus.login(
        {
          'webClientId': '732334025518-qntcjfqgp1vpl07ncj0qn809ujo3lpfu.apps.googleusercontent.com', // optional clientId of your Web application from Credentials settings of your project - On Android, this MUST be included to get an idToken. On iOS, it is not required.
          offline: true
        },
        function (obj) {
          alert(JSON.stringify(obj)); // do something useful instead of alerting
        },
        function (msg) {
          alert('error: ' + msg);
        }
    );
  }
})

.controller('ChatsCtrl', function($scope, Chats) {
  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //
  //$scope.$on('$ionicView.enter', function(e) {
  //});

  $scope.chats = Chats.all();
  $scope.remove = function(chat) {
    Chats.remove(chat);
  };
})

.controller('ChatDetailCtrl', function($scope, $stateParams, Chats) {
  $scope.chat = Chats.get($stateParams.chatId);
})

.controller('AccountCtrl', function($scope) {
  $scope.settings = {
    enableFriends: true
  };
});
