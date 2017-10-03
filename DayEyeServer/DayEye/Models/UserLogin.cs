using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace DayEye.Models
{
    public class UserLogin
    {
        public string Email { get; set; }
        public string AuthorizationToken { get; set; }
        public string FirstName { get; set; }
    }
}