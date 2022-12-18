using Newtonsoft.Json;
using System.Net;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class WikiDataGrabber
    {
        public string getDataFromLink(string url = null)
        {
            var httpRequest = (HttpWebRequest)WebRequest.Create(url);
            httpRequest.Accept = "application/json";
            var httpResponse = (HttpWebResponse)httpRequest.GetResponse();
            string result;
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                result = streamReader.ReadToEnd();
            }

            dynamic stuff = JsonConvert.DeserializeObject(result);

            var test1 = stuff.entities; // access element entities

            var test3 = url.Split('/').Last(); // extract uri from url

            var test4 = stuff.entities[test3]; // access elements/uri-which-is-just-a-string


            string description = stuff.entities[test3].descriptions.en.value;


            return description;
        }
    }
}
