using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace DayEye.DayEyeDb.Entities
{
    public class User
    {
        public string Email { get; set; }
        public string GoogleToken { get; set; }
        public string RefreshToken { get; set; }
        public string FirstName { get; set; }
    }
}