using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Net;
using System.Text.RegularExpressions;
using static MudBlazor.CategoryTypes;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class WikiDataGrabber
    {
        /// <summary>
        /// Gets data from a Wikidata URL and extracts required data from there. Currently only gets the
        /// description of an entry but in future it might do more/someting else. Eventually spltting it
        /// into separate methods might be advisable, like one for getting Wikidata description and another
        /// to get Wikipedia text.
        /// </summary>
        /// <param name="wikiDataUrl"></param> URL to Wikidata. If it's something else, the method immediately returns the content of url
        /// <param name="language"></param> Optional, as it defaults to english (en). You can choose which laguage your desired data should be returned in
        /// <returns></returns> Either the Wikidata description (currently) or the content of url if it's a non-url-string
        public List<string> GetDataFrom(string wikiDataUrl, string language = "en")
        {
            List<string> toolTipContent = new List<string>();
            if(!IsWikiDatalink(wikiDataUrl))
            {
                return toolTipContent;
            }

            wikiDataUrl = AdjustUrl(wikiDataUrl);

            dynamic wikiDataJsonFile = GetDataFromUrl(wikiDataUrl);
            string uri = ExtractUri(wikiDataUrl);
            string description = GetWikidataDescription(wikiDataJsonFile, uri);
            // If there is no Wikipedia URL for given WikiData entry...
            string wikipediaLink = GetWikipediaUrl(wikiDataJsonFile, uri, language);
            if(wikipediaLink==null)
            {
                // ...try to get the description instead...
                string descriptionFailsafe = GetWikidataDescription(wikiDataJsonFile, uri);
                if(descriptionFailsafe==null)
                {
                    //...and if there isn't even a description, just enter an empty string.
                    toolTipContent.Add("");
                }
                else
                {
                    toolTipContent.Add(descriptionFailsafe);
                }
            }
            else
            {
                wikipediaLink = AdjustWikipediaLink(wikipediaLink);
                try
                {
                    JObject wikipediaJsonFile = GetDataFromUrl(wikipediaLink)["query"]["pages"];
                    string pageId = wikipediaJsonFile.Properties().First().Name;
                    //Splitting the string, because it would show every section and we only want the first description
                    string extract = wikipediaJsonFile[pageId]["extract"].ToString().Split("\n\n\n==")[0];
                    toolTipContent.Add(extract);
                    string imageUrl = GetPictureUrlFromWikipedia(wikipediaLink);
                    toolTipContent.Add(imageUrl);
                }
                catch (System.Exception)
                {

                }

            }
            return toolTipContent;
        }

        /// <summary>
        /// Modifies the wikipedia link to get the image url
        /// </summary>
        /// <param name="adjustedUrl"></param>
        /// <returns></returns>
        public string GetPictureUrlFromWikipedia(string adjustedUrl)
        {
            adjustedUrl += "&prop=pageimages&format=json&pithumbsize=200";
            JObject wikipediaJsonResponse = GetDataFromUrl(adjustedUrl)["query"]["pages"];
            string pageId = wikipediaJsonResponse.Properties().First().Name;
            string imageUrl = wikipediaJsonResponse[pageId].ToString();
            return imageUrl.Contains("thumbnail") ? wikipediaJsonResponse[pageId]["thumbnail"]["source"].ToString() : "";
        }

        /// <summary>
        /// Gets Data from the url as a json object
        /// </summary>
        /// <param name="url"></param>
        /// <returns></returns>
        public static dynamic GetDataFromUrl(string url)
        {
            var httpRequest = (HttpWebRequest)WebRequest.Create(url);
            httpRequest.Accept = "application/json";
            var httpResponse = (HttpWebResponse)httpRequest.GetResponse();
            string result;
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                result = streamReader.ReadToEnd();
            }
            dynamic jsonObj = JsonConvert.DeserializeObject(result);
            return jsonObj;

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
        /// If not stated otherwise, take the english description
        /// </summary>
        /// <param name="jsonObject"></param> JSON Object with data from Wikidata Entry
        /// <param name="uri"></param> URI of the above mentioned Wikidata Entry
        /// <param name="language"></param> Optional, as it defaults to english (en). You can choose which laguage the description should be in
        /// <returns></returns> The description of the Wikidata Entry (directly from Wikidata, not Wikipedia), if none available - null
        public string GetWikidataDescription(dynamic jsonObject, string uri, string language = "en")
        {
            string description;
            try
            {
                description = jsonObject.entities[uri].descriptions[language].value;
            }
            catch
            {
                description = null;
            }
            return description;
        }

        /// <summary>
        /// If not stated otherwise, take the english Wikipedia link
        /// </summary>
        /// <param name="jsonObject"></param> JSON Object with data from Wikidata Entry
        /// <param name="uri"></param> URI of the previously mentioned Wikidata Entry
        /// <param name="language"></param> Optional, as it defaults to english (en). You can choose which laguage the Wikipedia Entry should be in
        /// <returns></returns> The Wikipedia URL, if none available - null
        public string GetWikipediaUrl(dynamic jsonObject, string uri, string language = "en")
        {
            string wikipediaUrl;
            try
            {
                wikipediaUrl = jsonObject.entities[uri].sitelinks[language + "wiki"].url;
            }
            catch
            {
                wikipediaUrl = null;
            }
            return wikipediaUrl;
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
        /// <summary>
        /// Adjusts Wikipedia Link which we got from Wikidata
        /// </summary>
        /// <param name="url"></param>
        /// <returns></returns>
        public static string AdjustWikipediaLink(string url) {
            string adjustedUrl = Regex.Replace(url, "/wiki/", "/w/api.php?format=json&action=query&prop=extracts&explaintext=1&titles=");
            return adjustedUrl;
        }
    }
}
