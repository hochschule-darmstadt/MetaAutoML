using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System.Net;
using System.Text.RegularExpressions;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public static class WikiDataGrabber
    {
        /// <summary>
        /// Gets data from a Wikidata URL and extracts required data from there. Currently only gets the
        /// description of an entry but in future it might do more/someting else. Eventually spltting it
        /// into separate methods might be advisable, like one for getting Wikidata description and another
        /// to get Wikipedia text.
        /// </summary>
        /// <param name="url"></param> URL to Wikidata. If it's something else, the method immediately returns the content of url
        /// <param name="language"></param> Optional, as it defaults to english (en). You can choose which laguage your desired data should be returned in
        /// <returns></returns> Either the Wikidata description (currently) or the content of url if it's a non-url-string
        public string GetDataFromUrl(string url, string language = "en")
        {
            if(!IsWikiDatalink(url))
            {
                return url;
            }
            
            url = AdjustUrl(url);

            var httpRequest = (HttpWebRequest)WebRequest.Create(url);
            httpRequest.Accept = "application/json";
            var httpResponse = (HttpWebResponse)httpRequest.GetResponse();
            string result;
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                result = streamReader.ReadToEnd();
            }

            dynamic jsonObject = StringToJsonObject(result);
            string uri = ExtractUri(url);
            string description = GetWikidataDescription(jsonObject, uri);

            return description;
        }
        /// <summary>
        /// Deserialize the JSON String to a JSON Object
        /// </summary>
        /// <param name="data"></param>JSON as a String
        /// <returns></returns>JSON as a (dynamically created) object
        public dynamic StringToJsonObject(string data)
        {
            dynamic jsonObject = JsonConvert.DeserializeObject(data);
            return jsonObject;
        }

        /// <summary>
        /// The URI will be needed to access the correct part of the JSON
        /// </summary>
        /// <param name="url"></param> Wikidata URL as a String e.g. https://www.wikidata.org/wiki/Q47509047
        /// <returns></returns>The URI of the Entry e.g. Q47509047
        public string ExtractUri(string url)
        {
            string uri = url.Split('/').Last();
            return uri;
        }

        /// <summary>
        /// if not stated otherwise, take the english description
        /// </summary>
        /// <param name="jsonObject"></param> JSON Object with data from Wikidata Entry
        /// <param name="uri"></param> URI of the above mentioned Wikidata Entry
        /// <param name="language"></param> Optional, as it defaults to english (en). You can choose which laguage the description should be in
        /// <returns></returns> The description of the Wikidata Entry (directly from Wikidata, not Wikipedia)
        public string GetWikidataDescription(dynamic jsonObject, string uri, string language = "en")
        {
            string description = jsonObject.entities[uri].descriptions[language].value;

            return description;
        }

        /// <summary>
        /// Simple Regex - if the url is already correct, nothing bad will happen. Wikidata Url needs to contain
        /// /entity/ instead of /wiki/ to return a JSON 
        /// </summary>
        /// <param name="url"></param> URL to the Wikidata Entry
        /// <returns></returns> Modified URL as described in summary
        public string AdjustUrl(string url)
        {
            string adjustedUrl = Regex.Replace(url, "/wiki/", "/entity/");
            return adjustedUrl;
        }

        /// <summary>
        /// Adds a little fail-safety. Why this method exists: While testing with ChipSet.razor I noticed, that a
        /// "chiptoadd" was not really a chip. Its tooltip text was
        /// "This strategy ignores certain dataset columns if they have been flagged as duplicate in the dataset analysis."
        /// I don't know the reason why this happens, so I added this failsafe instead.
        /// Update: In case of Chips it seems that sometimes they already have a tooltip. This failsafe might turn out
        /// really helpful in other cases too.
        /// </summary>
        /// <param name="url"></param> Some string, not necessarily an URL to Wikidata (but hopefully)
        /// <returns></returns> True if it really is a Wikidata Link, otherwise false
        public bool IsWikiDatalink(string url)
        {
            if(Regex.IsMatch(url, "https://www.wikidata.org/"))
            {
                return true;
            }
            return false;
        }

        public string GetWikipediaText(string url, string language = "en") {
            string adjustedUrl = Regex.Replace(url, "/wiki/", "/w/api.php?format=json&action=query&prop=extracts&explaintext=1&titles=");
            
        }
    }
}
