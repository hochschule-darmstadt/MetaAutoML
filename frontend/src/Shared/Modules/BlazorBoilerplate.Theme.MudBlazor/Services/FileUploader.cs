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
using Microsoft.AspNetCore.SignalR.Client;
using static MudBlazor.CategoryTypes;
using System.Net.Http;
using System.Diagnostics;
using System.IO;
using System.Net.Http.Headers;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class FileUploader : IFileUploader
    {
        private IApiClient _client;
        private IViewNotifier _notifier;
        private IStringLocalizer<Global> _l;
        private readonly NavigationManager _navigation;
        private HubConnection _uploadHubConnection;
        private HttpClient _httpClient;
        public FileUploader(IApiClient client, IViewNotifier notifier, NavigationManager navigation, IStringLocalizer<Global> L, HttpClient httpClient)
        {
            _client = client;
            _notifier = notifier;
            _l = L;
            _navigation = navigation;
            _httpClient = httpClient;
        }

        public async Task InitHub()
        {
            _uploadHubConnection = new HubConnectionBuilder()
                .WithUrl(new Uri(_httpClient.BaseAddress, Constants.HubPaths.Upload))
                .WithAutomaticReconnect()
                .Build();

            _uploadHubConnection.On<double>("UploadDatasetProgress", (progress) =>
            {
                // Handle progress update
                Progress = progress;
                UploadText = _l["Uploading {0} {1}", UploadDatasetRequest.DatasetName, String.Format("{0:0}", progress)];
                OnStateHasChangedCallback.Invoke();


            });

            _uploadHubConnection.On<string>("UploadDatasetComplete", (result) =>
            {
                // Handle download completion
                IsUploading = false;
                UploadText = "";
                Progress = 0;
                OnUploadCompletedCallback.Invoke();
                OnStateHasChangedCallback.Invoke();
            });

            _uploadHubConnection.Reconnected += connectionId =>
            {
                Console.WriteLine($"Reconnected with ConnectionId: {connectionId}");
                SignalRUploadFromDiskConnectionId = connectionId ?? string.Empty;
                // Optionally notify the server of reconnection or update UI
                return Task.CompletedTask;
            };

            await _uploadHubConnection.StartAsync();
            SignalRUploadFromDiskConnectionId = _uploadHubConnection.ConnectionId;
        }

        public UploadDatasetRequestDto UploadDatasetRequest { get; set; }
        public UploadPredictionRequestDto UploadPredictionRequest { get; set; }
        public IBrowserFile UploadFileContent { get; set; }
        public bool IsUploading { get; set; } = false;
        public double Progress { get; set; } = 0;
        public string UploadText { get; set; } = "";
        public Action OnUploadChangedCallback { get; set; }
        public Action OnStateHasChangedCallback { get; set; }
        public Action RefreshUploadComponentCallback { get; set; }
        public Func<Task> OnUploadCompletedCallback { get; set; }
        public bool IsUploadDatasetDialogOpen { get; set; } = false;
        public bool IsPredictionDatasetToUpload { get; set; } = false;
        public bool IsUploadPredictionDatasetDialogOpen { get; set; } = false;

        public string SignalRUploadFromDiskConnectionId { get; set; } = "";

        public string SignalRUploadFromUrlConnectionId { get; set; } = "";

        /// <summary>
        /// Upload a dataset from local storage
        /// </summary>
        /// <returns></returns>
        public async Task UploadDatasetFromDisk()
        {
            IsUploading = true;

            try
            {
                if (UploadFileContent.Size > 500 * 1024 * 1024)
                {
                    _notifier.Show(_l["File is too large. Please use a URL for files larger than 500MB"], ViewNotifierType.Warning);
                    return;
                }
                var content = new MultipartFormDataContent();
                var fileContent = new StreamContent(UploadFileContent.OpenReadStream(int.MaxValue));
                fileContent.Headers.ContentType = new MediaTypeHeaderValue(UploadFileContent.ContentType);
                content.Add(fileContent, "file", UploadFileContent.Name);
                content.Add(new StringContent(UploadDatasetRequest.DatasetName), "datasetName");
                content.Add(new StringContent(UploadDatasetRequest.DatasetType), "datasetType");
                content.Add(new StringContent(SignalRUploadFromDiskConnectionId), "signalrConnectionId");

                var response = await _client.UploadFromDisk(content);

                if (!response.IsSuccessStatusCode)
                {
                    _notifier.Show(_l[response.Message], ViewNotifierType.Error, _l["Operation Failed"]);
                }
            }
            catch (Exception ex)
            {
                _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            }
            finally
            {
                IsUploading = false;
            }
            //IsUploading = true;
            //try
            //{
            //    using (StreamReader reader = new StreamReader(UploadFileContent.OpenReadStream(long.MaxValue)))
            //    {
            //        await UploadFileToServer(reader);
            //    }
            //}
            //catch (Exception ex)
            //{
            //    _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            //}
            //return;
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

            var request = new UploadDatasetRequestDto
            {
                Url = url,
                DatasetName = UploadDatasetRequest.DatasetName,
                DatasetType = UploadDatasetRequest.DatasetType,
                SignalrConnectionId = SignalRUploadFromDiskConnectionId

            };

            var response = await _client.UploadFromUrl(request);

            if (!response.IsSuccessStatusCode)
            {
                IsUploading = false;
                _notifier.Show(_l["A file could not be downloaded from this URL!"], ViewNotifierType.Error, _l["Operation Failed"]);
            }
            //IsUploading = true;
            //string _downloadUrl = GetDownloadUrl(url);
            //try
            //{
            //    using (var client = new HttpClient())
            //    {
            //        HttpResponseMessage response = await client.GetAsync(_downloadUrl);
            //        response.EnsureSuccessStatusCode();

            //        // Get the file extension from content disposition header
            //        string _fileExtension =
            //            (response.Content.Headers.ContentDisposition?.FileNameStar ??
            //            response.Content.Headers.ContentDisposition?.FileName)?
            //            .Split('.').LastOrDefault()?.TrimEnd('"') ?? string.Empty;
            //        fileType = !string.IsNullOrEmpty(_fileExtension) ? $".{_fileExtension}" : fileType.Split(',')[0];
            //        UploadDatasetRequest.FileNameOrURL = UploadDatasetRequest.DatasetName + fileType;

            //        using (Stream contentStream = await response.Content.ReadAsStreamAsync())
            //        {
            //            using (StreamReader reader = new StreamReader(contentStream))
            //            {
            //                await UploadFileToServer(reader);
            //            }
            //        }
            //    }
            //    return;
            //}
            //catch (Exception ex)
            //{
            //    _notifier.Show(_l["A file could not be downloaded from this URL!"], ViewNotifierType.Error, _l["Operation Failed"]);
            //    _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            //}

        }

        /// Uploads a file to the MongoDB server.
        /// </summary>
        /// <param name="reader">The StreamReader containing the file to upload.</param>
        /// <returns></returns>
        //private async Task UploadFileToServer(StreamReader reader)
        //{
        //    int chunkSize = 1000000;
        //    long bytesRead = 0;

        //    MemoryStream ms = new MemoryStream();
        //    await reader.BaseStream.CopyToAsync(ms);
        //    ms.Seek(0, SeekOrigin.Begin);
        //    if ((ms.Length % chunkSize) == 0) //no extra chunk
        //    {
        //        if (IsPredictionDatasetToUpload == true)
        //        {
        //            UploadPredictionRequest.TotalChunkNumber = (int)(ms.Length / chunkSize);
        //        }
        //        else
        //        {
        //            UploadDatasetRequest.TotalChunkNumber = (int)(ms.Length / chunkSize);
        //        }
        //    }
        //    else
        //    {
        //        if (IsPredictionDatasetToUpload == true)
        //        {
        //            UploadPredictionRequest.TotalChunkNumber = (int)(ms.Length / chunkSize) + 1; //append extra chunk
        //        }
        //        else
        //        {
        //            UploadDatasetRequest.TotalChunkNumber = (int)(ms.Length / chunkSize) + 1; //append extra chunk
        //        }
        //    }
        //    if (IsPredictionDatasetToUpload == true)
        //    {
        //        UploadPredictionRequest.ChunkNumber = 1;
        //    }
        //    else
        //    {
        //        UploadDatasetRequest.ChunkNumber = 1;
        //    }

        //    while (bytesRead < ms.Length)
        //    {
        //        var bytesToRead = ms.Length - bytesRead;
        //        var bufferSize = Math.Min(chunkSize, bytesToRead);
        //        var buffer = new byte[bufferSize];
        //        var reallyRead = ms.Read(buffer, 0, buffer.Length);
        //        if (IsPredictionDatasetToUpload == true)
        //        {
        //            UploadPredictionRequest.Content = buffer;
        //        }
        //        else
        //        {
        //            UploadDatasetRequest.Content = buffer;
        //        }


        //        ApiResponseDto apiResponse = new ApiResponseDto();

        //        if (IsPredictionDatasetToUpload == true)
        //        {
        //            apiResponse = await _client.UploadPrediction(UploadPredictionRequest);
        //        }
        //        else
        //        {
        //            apiResponse = await _client.UploadDataset(UploadDatasetRequest);
        //        }

        //        if (!apiResponse.IsSuccessStatusCode)
        //        {
        //            _notifier.Show(_l[apiResponse.Message] + " : " + apiResponse.StatusCode, ViewNotifierType.Error, _l["Operation Failed"]);
        //        }

        //        if (apiResponse.StatusCode == Status406NotAcceptable)
        //        {
        //            // If the Dataset is not structured correctly, stop the upload and do not safe it
        //            break;
        //        }

        //        bytesRead += reallyRead;
        //        if (IsPredictionDatasetToUpload == true)
        //        {
        //            UploadPredictionRequest.ChunkNumber++;
        //        }
        //        else
        //        {
        //            UploadDatasetRequest.ChunkNumber++;
        //        }

        //        if (OnUploadChangedCallback != null)
        //        {
        //            OnUploadChangedCallback();
        //        }

        //    }
        //    IsUploading = false;
        //    if (OnUploadChangedCallback != null)
        //    {
        //        OnUploadChangedCallback();
        //    }
        //    if (OnUploadCompletedCallback != null)
        //    {
        //        await OnUploadCompletedCallback();
        //    }
        //    return;
        //}

    }
}
