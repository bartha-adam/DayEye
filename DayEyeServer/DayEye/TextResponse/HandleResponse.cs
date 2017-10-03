using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace DayEye.TextResponse
{
    public class HandleResponse
    {

        private string LateNoEvents = "Hello {0}. You don't have any more events today, also, it's getting quite late, so you might as well go grab a cold one from upstairs.";
        private string SoonEventTemplate = "Hello {0}. You have {1} in {2} minutes.";
        private string LateEventTemplate = "Hello {0}. You are free for the next {1} minutes. So grab a cup of coffee, and prepair for the day.";
        private string EventUndergoingTemplate = "Hello {0}, you are currently missing an undergoing {1}, which has started {2} minutes ago. Please hurry, so you won't completely miss it.";
        private string EarlyNoEvents = "Hello {0}. You have no events in the next hour, so feel free to relax.";

        public string CreateTextResponse(JObject jsonData, string name)
        {
            var events = jsonData["items"];

            if (events.Count() == 0)
            {
                if(DateTime.Now.Hour > 22 || DateTime.Now.Hour < 9)
                {
                    return string.Format(LateNoEvents, name);
                }

                return string.Format(EarlyNoEvents, name);
            }
            else
            {

                var eventSummary = (string)jsonData["items"][0]["summary"];
                var startTime = (DateTime)jsonData["items"][0]["start"]["dateTime"];

                var timeDifference = startTime - DateTime.Now;

                if(timeDifference.Minutes < 0)
                {

                    return string.Format(EventUndergoingTemplate, name, eventSummary, (-1) * timeDifference.Minutes);

                }
                else if(timeDifference.Minutes > 30)
                {
                    return string.Format(LateEventTemplate, name, timeDifference.Minutes);
                }

                return string.Format(SoonEventTemplate, name, eventSummary, timeDifference.Minutes);
            }

        }

    }
}