define(function () {
    return {
        getConfig: function(callback) {
          $.ajax({
            contentType: "application/json",
            url: '/config',
            success: function(data) {
              callback(data);
            }
          });
        },
       registerFace: function (data, callback) {
         $.ajax({
           url: '/face/register',
           type: 'POST',
           data: data,
           success: function(data) {
             console.log(data)
             callback(data);
           },
           dataType: "application/json"
         });
       }
    };
});
