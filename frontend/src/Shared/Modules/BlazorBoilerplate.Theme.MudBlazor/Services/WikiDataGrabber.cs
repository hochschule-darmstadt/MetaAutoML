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
            return result;
        }
    }
}
