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
        public async Task UploadDatasetFromLocal()
        {
            int chunkSize = 1000000;
            long bytesRead = 0;
            byte[] data = new byte[chunkSize];
            IsUploading = true;
            try
            {
                MemoryStream ms = new MemoryStream();
                StreamReader reader = new StreamReader(UploadFileContent.OpenReadStream(long.MaxValue));
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
            }
            catch (Exception ex)
            {
                _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            }
            return;
        }
        public async Task UploadDatasetFromURL(string url, string fileType)
        {
            int chunkSize = 1000000;
            long bytesRead = 0;

            try
            {
                using (var client = new HttpClient())
                {
                    using (var s = client.GetStreamAsync(url))
                    {
                        using (var fs = new FileStream("localfile" + fileType, FileMode.OpenOrCreate))
                        {
                            s.Result.CopyTo(fs);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _notifier.Show(_l["A file could not be downloaded from this URL!"], ViewNotifierType.Error, _l["Operation Failed"]);
                _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            }

            MemoryStream ms = new MemoryStream();
            StreamReader reader = new StreamReader("localfile" + fileType);
            await reader.BaseStream.CopyToAsync(ms);
            ms.Seek(0, SeekOrigin.Begin);

            UploadDatasetRequest.FileNameOrURL = UploadDatasetRequest.DatasetName + fileType;

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
            if (File.Exists("localfile" + fileType))
            {
                File.Delete("localfile" + fileType);
            }
        }
        public string GetDownloadUrl(string url)
        {
            if (Regex.IsMatch(url, @"(?:drive\.google\.com)"))
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
            return url;
        }
        private static string GetGoogleDriveDownloadLink(string googleDriveUrl)
        {
            var match = Regex.Match(googleDriveUrl, @"/d/([a-zA-Z0-9_-]+)");
            if (match.Success && match.Groups.Count > 1)
            {
                string fileId = match.Groups[1].Value;
                googleDriveUrl = $"https://drive.google.com/uc?id={fileId}&export=download";
                return googleDriveUrl;
            }
            return googleDriveUrl;
            //throw new InvalidOperationException("Unable to extract Google Drive file ID from the URL");
        }

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

        private static string GetOnedriveDownloadLink(string onedriveUrl)
        {
            string base64Value = System.Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(onedriveUrl));
            string encodedUrl = base64Value.TrimEnd('=').Replace('/', '_').Replace('+', '-');
            onedriveUrl = $"https://api.onedrive.com/v1.0/shares/u!{encodedUrl}/root/content";
            return onedriveUrl;
        }

        private static string GetSharepointDownloadLink(string sharepointUrl)
        {
            if (sharepointUrl.Contains("&download=1"))
            {
                return sharepointUrl;
            }
            return sharepointUrl + "&download=1";
        }

        private static string GetNextcloudDownloadLink(string nextcloudUrl)
        {
            if (nextcloudUrl.EndsWith("/download"))
            {
                return nextcloudUrl;
            }
            return nextcloudUrl + "/download";
        }
    }
}
