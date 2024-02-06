using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Grpc.Net.Client;
using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.Extensions.Localization;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Components;
using BlazorBoilerplate.Shared.Dto.Prediction;
//using HtmlAgilityPack;
using static Microsoft.AspNetCore.Http.StatusCodes;
using System.Net;
using System.Text.Json;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class FileUploader : IFileUploader
    {
        private IApiClient _client;
        private IViewNotifier _notifier;
        private IStringLocalizer<Global> _l;
        public FileUploader(IApiClient client, IViewNotifier notifier, IStringLocalizer<Global> L)
        {
            _client = client;
            _notifier = notifier;
            _l = L;
        }
        public UploadDatasetRequestDto UploadDatasetRequest { get; set; }
        public UploadPredictionRequestDto UploadPredictionRequest { get; set; }
        public IBrowserFile UploadFileContent { get; set; }
        public bool IsUploading { get; set; } = false;
        public Action OnUploadChangedCallback { get; set; }
        public Action RefreshUploadComponentCallback { get; set; }
        public Func<Task> OnUploadCompletedCallback { get; set; }
        public bool IsUploadDatasetDialogOpen { get; set; } = false;
        public bool IsPredictionDatasetToUpload { get; set; } = false;
        public bool IsUploadPredictionDatasetDialogOpen { get; set; } = false;

        /// <summary>
        /// Upload a dataset from local storage
        /// </summary>
        /// <returns></returns>
        public async Task UploadDatasetFromLocal()
        {
            IsUploading = true;
            try
            {
                using (StreamReader reader = new StreamReader(UploadFileContent.OpenReadStream(long.MaxValue)))
                {
                    await UploadFileToServer(reader);
                }
            }
            catch (Exception ex)
            {
                _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            }
            return;
        }

        /// <summary>
        /// Upload a dataset from a given URL, also try to get the file extension from the HTTP header
        /// </summary>
        /// <param name="url">Direct download URL of a dataset.</param>
        /// <param name="fileType">The file type of the dataset.</param>
        /// <returns></returns>
        public async Task UploadDatasetFromURL(string url, string fileType)
        {
            IsUploading = true;
            string _downloadUrl = GetDownloadUrl(url);
            try
            {
                using (var client = new HttpClient())
                {
                    HttpResponseMessage response = await client.GetAsync(_downloadUrl);
                    response.EnsureSuccessStatusCode();

                    // Get the file extension from content disposition header
                    string _fileExtension =
                        (response.Content.Headers.ContentDisposition?.FileNameStar ??
                        response.Content.Headers.ContentDisposition?.FileName)?
                        .Split('.').LastOrDefault()?.TrimEnd('"') ?? string.Empty;
                    fileType = !string.IsNullOrEmpty(_fileExtension) ? $".{_fileExtension}" : fileType.Split(',')[0];
                    UploadDatasetRequest.FileNameOrURL = UploadDatasetRequest.DatasetName + fileType;

                    using (Stream contentStream = await response.Content.ReadAsStreamAsync())
                    {
                        using (StreamReader reader = new StreamReader(contentStream))
                        {
                            await UploadFileToServer(reader);
                        }
                    }
                }
                return;
            }
            catch (Exception ex)
            {
                _notifier.Show(_l["A file could not be downloaded from this URL!"], ViewNotifierType.Error, _l["Operation Failed"]);
                _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            }

        }

        /// Uploads a file to the MongoDB server.
        /// </summary>
        /// <param name="reader">The StreamReader containing the file to upload.</param>
        /// <returns></returns>
        private async Task UploadFileToServer(StreamReader reader)
        {
            int chunkSize = 1000000;
            long bytesRead = 0;

            MemoryStream ms = new MemoryStream();
            await reader.BaseStream.CopyToAsync(ms);
            ms.Seek(0, SeekOrigin.Begin);
            if ((ms.Length % chunkSize) == 0) //no extra chunk
            {
                if (IsPredictionDatasetToUpload == true)
                {
                    UploadPredictionRequest.TotalChunkNumber = (int)(ms.Length / chunkSize);
                }
                else
                {
                    UploadDatasetRequest.TotalChunkNumber = (int)(ms.Length / chunkSize);
                }
            }
            else
            {
                if (IsPredictionDatasetToUpload == true)
                {
                    UploadPredictionRequest.TotalChunkNumber = (int)(ms.Length / chunkSize) + 1; //append extra chunk
                }
                else
                {
                    UploadDatasetRequest.TotalChunkNumber = (int)(ms.Length / chunkSize) + 1; //append extra chunk
                }
            }
            if (IsPredictionDatasetToUpload == true)
            {
                UploadPredictionRequest.ChunkNumber = 1;
            }
            else
            {
                UploadDatasetRequest.ChunkNumber = 1;
            }

            while (bytesRead < ms.Length)
            {
                var bytesToRead = ms.Length - bytesRead;
                var bufferSize = Math.Min(chunkSize, bytesToRead);
                var buffer = new byte[bufferSize];
                var reallyRead = ms.Read(buffer, 0, buffer.Length);
                if (IsPredictionDatasetToUpload == true)
                {
                    UploadPredictionRequest.Content = buffer;
                }
                else
                {
                    UploadDatasetRequest.Content = buffer;
                }


                ApiResponseDto apiResponse = new ApiResponseDto();

                if (IsPredictionDatasetToUpload == true)
                {
                    apiResponse = await _client.UploadPrediction(UploadPredictionRequest);
                }
                else
                {
                    apiResponse = await _client.UploadDataset(UploadDatasetRequest);
                }

                if (!apiResponse.IsSuccessStatusCode)
                {
                    _notifier.Show(_l[apiResponse.Message] + " : " + apiResponse.StatusCode, ViewNotifierType.Error, _l["Operation Failed"]);
                }

                if (apiResponse.StatusCode == Status406NotAcceptable)
                {
                    // If the Dataset is not structured correctly, stop the upload and do not safe it
                    break;
                }

                bytesRead += reallyRead;
                if (IsPredictionDatasetToUpload == true)
                {
                    UploadPredictionRequest.ChunkNumber++;
                }
                else
                {
                    UploadDatasetRequest.ChunkNumber++;
                }

                if (OnUploadChangedCallback != null)
                {
                    OnUploadChangedCallback();
                }

            }
            IsUploading = false;
            if (OnUploadChangedCallback != null)
            {
                OnUploadChangedCallback();
            }
            if (OnUploadCompletedCallback != null)
            {
                await OnUploadCompletedCallback();
            }
            return;
        }

        /// <summary>
        /// Get the download URL for a given URL of supported cloud storage services
        /// </summary>
        /// <param name="url">The URL entered by the user.</param>
        /// <returns>direct download link</returns>
        private static string GetDownloadUrl(string url)
        {
            if (Regex.IsMatch(url, @"(?:drive\.google\.com|docs\.google\.com)"))
            {
                return GetGoogleDriveDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:\.dropbox\.com)"))
            {
                return GetDropboxDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:1drv\.ms|i\.s!)"))
            {
                return GetOnedriveDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:sharepoint\.com)"))
            {
                return GetSharepointDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:cloud\.h-da\.de)"))
            {
                return GetNextcloudDownloadLink(url);
            }
            if (Regex.IsMatch(url, @"(?:openml\.org/search).*type=data"))
            {
                return GetOpenMLDownloadLink(url);
            }
            return url;
        }
        /// <summary>
        /// Get the direct download URL for Google Drive using the file id
        /// </summary>
        /// <param name="googleDriveUrl">Google Drive URL</param>
        /// <returns>Direct download URL for Google Drive</returns>
        private static string GetGoogleDriveDownloadLink(string googleDriveUrl)
        {
            var match = Regex.Match(googleDriveUrl, @"/d/([a-zA-Z0-9_-]+)");
            if (match.Success && match.Groups.Count > 1)
            {
                string fileId = match.Groups[1].Value;
                googleDriveUrl = $"https://drive.google.com/uc?id={fileId}&export=download&confirm=t";
                return googleDriveUrl;
            }
            return googleDriveUrl;
        }

        /// <summary>
        /// Get the direct download URL for Dropbox
        /// </summary>
        /// <param name="dropboxUrl">Dropbox URL</param>
        /// <returns>Direct Download URL for Dropbox</returns>
        private static string GetDropboxDownloadLink(string dropboxUrl)
        {
            if (dropboxUrl.EndsWith("&dl=0"))
            {
                return dropboxUrl.Replace("&dl=0", "&dl=1");
            }
            if (!dropboxUrl.EndsWith("&dl=1"))
            {
                return dropboxUrl + "&dl=1";
            }
            return dropboxUrl;
        }

        /// <summary>
        /// Get the direct download URL for OneDrive by encoding the Base64 decoded URL
        /// </summary>
        /// <param name="onedriveUrl">OneDrive URL</param>
        /// <returns>Direct download URL for Onedrive</returns>
        private static string GetOnedriveDownloadLink(string onedriveUrl)
        {
            string base64Value = System.Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(onedriveUrl));
            string encodedUrl = base64Value.TrimEnd('=').Replace('/', '_').Replace('+', '-');
            onedriveUrl = $"https://api.onedrive.com/v1.0/shares/u!{encodedUrl}/root/content";
            return onedriveUrl;
        }

        /// <summary>
        /// Get the direct download URL for Sharepoint
        /// </summary>
        /// <param name="sharepointUrl">Sharepoint URL</param>
        /// <returns>Direct download URL for Sharepoint</returns>
        private static string GetSharepointDownloadLink(string sharepointUrl)
        {
            if (sharepointUrl.Contains("&download=1"))
            {
                return sharepointUrl;
            }
            return sharepointUrl + "&download=1";
        }

        /// <summary>
        /// Get the direct download URL for h_da Nextcloud
        /// </summary>
        /// <param name="nextcloudUrl">h_da Nextcloud URL</param>
        /// <returns>Direct download URL for h_da Nextcloud</returns>
        private static string GetNextcloudDownloadLink(string nextcloudUrl)
        {
            if (nextcloudUrl.EndsWith("/download"))
            {
                return nextcloudUrl;
            }
            return nextcloudUrl + "/download";
        }

        /// <summary>
        /// Get the direct download URL for OpenML datasets by using the OpenML API
        /// </summary>
        /// <param name="openMLUrl">OpenML URL</param>
        /// <returns>Direct download URL for OpenML datasets</returns>
        private static string GetOpenMLDownloadLink(string openMLUrl)
        {
            var match = Regex.Match(openMLUrl, @"(?:\b|\?)id=(\d+)\b");
            if (match.Success)
            {
                string datasetId = match.Groups[1].Value;
                string apiUrl = $"https://www.openml.org/api/v1/json/data/{datasetId}";
                try
                {
                    using (var client = new HttpClient())
                    {
                        HttpResponseMessage response = client.GetAsync(apiUrl).Result;
                        if (response.IsSuccessStatusCode)
                        {
                            JsonDocument jsonDocument = JsonDocument.Parse(response.Content.ReadAsStringAsync().Result);
                            JsonElement urlElement = jsonDocument.RootElement.GetProperty("data_set_description").GetProperty("url");
                            openMLUrl = urlElement.GetString();
                            return openMLUrl;
                        }
                    }
                }
                catch (Exception ex)
                {
                }
            }
            return openMLUrl;
        }
    }
}
