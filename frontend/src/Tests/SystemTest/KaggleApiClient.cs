using System.Net.Http.Headers;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace SystemTest
{
    /// <summary>
    ///  Provides functionality to list and download kaggle competition datasets.
    ///  Note that the account used for downloading the data has to have agreed to the terms for the competition data.
    /// </summary>
    internal class KaggleApiClient
    {
        private const string _baseApiUrl = "https://www.kaggle.com/api/v1/competitions/data/";
        private readonly HttpClient _client = new HttpClient();

        /// <summary>
        /// Initializes the client by authorizing with the credentials in auth/kaggle.json.
        /// </summary>
        public KaggleApiClient()
        {
            string rootDirectory = AppDomain.CurrentDomain.BaseDirectory;
            rootDirectory = rootDirectory[..(rootDirectory.IndexOf("frontend"))];
            string authDir = string.Format($"{rootDirectory}\\auth\\kaggle.json", rootDirectory);
            init(authDir);
        }

        /// <summary>
        /// Initializes the client by authorizing with the credentials from the kaggle.json
        /// </summary>
        /// <param name="authDir">The absolut path to the kaggle.json file</param>
        public KaggleApiClient(string authDir)
        {
            init(authDir);
        }

        private void init(string authDir)
        {
            var auth = new { Username = string.Empty, Key = string.Empty };

            using (var reader = new StreamReader(authDir))
            {
                var json = reader.ReadToEnd();
                auth = JsonConvert.DeserializeAnonymousType(json, auth);
            }

            var authToken = Convert.ToBase64String(
                Encoding.ASCII.GetBytes(
                    string.Format($"{auth.Username}:{auth.Key}", auth)
            ));

            _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", authToken);
        }

        /// <summary>
        /// Calls the Kaggle API to retrieve the names of the available data files/ folders of a competition.
        /// </summary>
        /// <param name="competitionName">Name of the competition whos data should be downloaded.</param>
        /// <returns>A list with the names of the datasets the Kaggle competition contains.</returns>
        public async Task<List<string>> ListCompetitionDatasets(string competitionName)
        {
            try
            {
                var json = await _client.GetStringAsync(
                        _baseApiUrl + "list/" + competitionName);
                JArray jsonArray = JArray.Parse(json);
                List<JToken> nameList = jsonArray.SelectTokens(@"$.[?(@.name != '')].name").ToList();

                return nameList.Values<string>().ToList();
            }
            catch(Exception ex)
            {
                Console.WriteLine($"Exception getting list of competition datasets. Exception:\n{ex.Message}");
            }
            return new List<string>();
        }

        /// <summary>
        /// Calls the Kaggle API to download all available data files/ folders of a competition to a desired folder.
        /// The data will be within a folder with the name of the competition.
        /// </summary>
        /// <param name="downloadDir">The absolute path to the directory where the data should be downloaded</param>
        /// <param name="competitionName">Name of the Kaggle competition</param>
        /// <returns>Returns a completed threading task</returns>
        public async Task<bool> DownloadCompetitionData(string downloadDir, string competitionName)
        {
            bool success = false;

            downloadDir = downloadDir + "\\" + competitionName;
            if (!Directory.Exists(downloadDir))
                Directory.CreateDirectory(downloadDir);
       
            List<string> datasetNames = await ListCompetitionDatasets(competitionName);
            foreach (string fileName in datasetNames)
            {
                if (File.Exists(downloadDir + "\\" + fileName))
                    break;

                success = await DownloadDataFile(downloadDir, competitionName, fileName);
            }

            return success;
        }

        /// <summary>
        /// Calls the Kaggle API to download a data file/ folder of a competition to a desired folder.
        /// </summary>
        /// <param name="downloadDir">The absolute path to the directory where the data should be downloaded</param>
        /// <param name="competitionName">Name of the Kaggle competition</param>
        /// <param name="fileName">Name of the file/ folder to be downloaded</param>
        /// <returns>Returns a completed threading task</returns>
        public async Task<bool> DownloadDataFile(string downloadDir, string competitionName, string fileName)
        {
            if (File.Exists(downloadDir + "\\" + fileName))
                return false;

            bool success = true;
            try
            {
                CancellationTokenSource timeoutTokenSource = new(TimeSpan.FromDays(1));
                using var stream = await _client.GetStreamAsync(
                    _baseApiUrl +
                    "download/" +
                    competitionName +
                    "/" +
                    fileName,
                    timeoutTokenSource.Token
                    );
                using var output = new FileStream(downloadDir + "\\" + fileName, FileMode.CreateNew);
                stream.CopyTo(output);
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"Download of {competitionName}-{fileName} failed, HTTP Status code: {ex.StatusCode}");
                success = false;
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine($"Download of {competitionName}-{fileName} timed out.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Unknown exception downloading dataset {competitionName}-{fileName}. Exception:\n{ex.Message}");
            }
            return success;
        }
    }
}
