using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System.Net;
using System.Text.RegularExpressions;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class WikiDataGrabber
    {
        public string getDataFromUrl(string url, string language = "en")
        {
            if(!isWikiDatalink(url))
            {
                return url;
            }
            
            url = adjustUrl(url);

            var httpRequest = (HttpWebRequest)WebRequest.Create(url);
            httpRequest.Accept = "application/json";
            var httpResponse = (HttpWebResponse)httpRequest.GetResponse();
            string result;
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                result = streamReader.ReadToEnd();
            }

            dynamic jsonObject = stringToJsonObject(result);
            string uri = extractUri(url);
            string description = getWikidataDescription(jsonObject, uri);

            return description;
        }

        // Deserialize the JSON String to a JSON Object
        public dynamic stringToJsonObject(string data)
        {
            dynamic jsonObject = JsonConvert.DeserializeObject(data);
            return jsonObject;
        }

        // The URI will be needed to access the correct part of the JSON
        public string extractUri(string url)
        {
            string uri = url.Split('/').Last();
            return uri;
        }

        // if not stated otherwise, take the english description
        public string getWikidataDescription(dynamic jsonObject, string uri, string language = "en")
        {
            string description = jsonObject.entities[uri].descriptions[language].value;

            return description;
        }

        // Simple Regex - if the url is already correct, nothing bad will happen. Wikidata Url needs to contain
        // /entity/ instead of /wiki/ to return a JSON 
        public string adjustUrl(string url)
        {
            string adjustedUrl = Regex.Replace(url, "/wiki/", "/entity/");
            return adjustedUrl;
        }

        // Adds a little fail-safety. Why this method exists: While testing with ChipSet.razor I noticed, that a
        // "chiptoadd" was not really a chip. Its tooltip text was
        // "This strategy ignores certain dataset columns if they have been flagged as duplicate in the dataset analysis."
        // I don't know the reason why this happens, so I added this failsafe instead.
        // Update: In case of Chips it seems that sometimes they already have a tooltip. This failsafe might turn out
        // really helpful in other cases too.
        public bool isWikiDatalink(string url)
        {
            if(Regex.IsMatch(url, "https://www.wikidata.org/"))
            {
                return true;
            }
            return false;
        }
    }
}
