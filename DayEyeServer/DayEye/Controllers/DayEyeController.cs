using DayEye.DayEyeDb;
using DayEye.DayEyeDb.Entities;
using DayEye.Models;
using DayEye.TextResponse;
using Newtonsoft.Json.Linq;
using System;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Web.Http;
using System.Web.Http.Cors;

namespace DayEye.Controllers
{

    public class DayEyeController : ApiController
    {

        [HttpPost]
        [Route("login")]
        [EnableCors(origins: "*", headers: "*", methods: "*")]
        public void AddNewUser(UserLogin login)
        { 

            var urlBuilder = new StringBuilder();
            urlBuilder.Append("https://");
            urlBuilder.Append("www.googleapis.com");
            urlBuilder.Append("/oauth2/v4/token");

            var httpWebRequest = HttpWebRequest.Create(urlBuilder.ToString()) as HttpWebRequest;

            httpWebRequest.Method = "POST";
            httpWebRequest.CookieContainer = new CookieContainer();

            httpWebRequest.ContentType = "application/x-www-form-urlencoded";
            httpWebRequest.Host = "www.googleapis.com";
            httpWebRequest.UserAgent = "DayEye";

            var dataBuilder = new StringBuilder();

            dataBuilder.Append("code=" + login.AuthorizationToken);
            dataBuilder.Append("&redirect_uri=");
            dataBuilder.Append("&client_id=" + "732334025518-n3k25bq7i5dukicc2oj0steuh61uj961.apps.googleusercontent.com");
            dataBuilder.Append("&client_secret=" + "eQh3m53wQ4wFTk0MF8OWvzeu");
            dataBuilder.Append("&scope=&grant_type=authorization_code");

            string postData = dataBuilder.ToString();

            httpWebRequest.ContentLength = postData.Length;

            using (StreamWriter requestWriter = new StreamWriter(httpWebRequest.GetRequestStream()))
            {
                requestWriter.Write(postData);
            }

            var response = httpWebRequest.GetResponse();
            var responseStream = response.GetResponseStream();
            StreamReader readStream = new StreamReader(responseStream, Encoding.UTF8);

            JObject json = JObject.Parse(readStream.ReadToEnd());

            
            
            using (var dbContext = new DayEyeDbContext())
            {
                var user = dbContext.Users.Where(x => x.Email.Equals(login.Email)).FirstOrDefault();

                if (user == null)
                {
                    var userToAdd = new User()
                    {
                        Email = login.Email,
                        GoogleToken = json.GetValue("access_token").ToString(),
                        RefreshToken = "none",
                        FirstName = login.FirstName
                    };

                    dbContext.Users.Add(userToAdd);

                    dbContext.SaveChanges();

                }
                else
                {

                    user.GoogleToken = json.GetValue("access_token").ToString();
                    user.FirstName = login.FirstName;

                    dbContext.SaveChanges();

                }

            }

            

        }

        [HttpPost]
        [Route("detected")]
        [EnableCors(origins: "*", headers: "*", methods: "*")]
        public HttpResponseMessage Detected(DetectedUser detected)
        {

            using (var dbContext = new DayEyeDbContext())
            {

                var user = dbContext.Users.Where(u => u.Email.Equals(detected.Email)).FirstOrDefault();

                if (user != null)
                {

                    /*
                     * Using the google token from the db, make a call to the calendar, get info about
                     * the user's activities, generate an mp3 file using the-to-speech and return it.
                     */

                    var accessToken = user.GoogleToken;

                    var urlBuilder = new StringBuilder();

                    urlBuilder.Append("https://");
                    urlBuilder.Append("www.googleapis.com");
                    urlBuilder.Append("/calendar/v3/calendars/primary/events");
                    urlBuilder.Append("?minAccessRole=writer");
                    urlBuilder.Append("&timeMin=" + Rfc3339.Rfc3339DateTime.ToString(DateTime.UtcNow));

                    var timeMax = DateTime.UtcNow;

                    urlBuilder.Append("&timeMax=" + Rfc3339.Rfc3339DateTime.ToString(timeMax.AddHours(1)));
                    urlBuilder.Append("&orderBy=startTime");
                    urlBuilder.Append("&singleEvents=True");

                    var httpWebRequest = HttpWebRequest.Create(urlBuilder.ToString()) as HttpWebRequest;

                    httpWebRequest.CookieContainer = new CookieContainer();
                    httpWebRequest.Headers["Authorization"] = string.Format("Bearer {0}", accessToken);
                    httpWebRequest.ContentType = "application/json; charset=utf-8";
                    WebResponse response;

                    try
                    {
                        response = httpWebRequest.GetResponse();

                    }catch(Exception e)
                    {
                        return Request.CreateResponse(HttpStatusCode.OK, "Please register again in the mobile app, your access code has expired!");
                    }

                    var responseStream = response.GetResponseStream();
                    StreamReader readStream = new StreamReader(responseStream, Encoding.UTF8);

                    string jsonString = readStream.ReadToEnd();

                    //var objects = JArray.Parse(jsonString);

                    JObject json = JObject.Parse(jsonString);

                    var textResponse = new HandleResponse();

                    //return Request.CreateResponse(HttpStatusCode.OK, json);

                    return Request.CreateResponse(HttpStatusCode.OK, textResponse.CreateTextResponse(json, user.FirstName));
                    
                }

            }

            return Request.CreateResponse(HttpStatusCode.OK, "Hello, you seem to not be registered in our application. Please register in order to enjoy our app.");

        }

    }
}