using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grpc.Net.Client;
using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.Extensions.Localization;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Components;
using BlazorBoilerplate.Shared.Dto.Prediction;
using static Microsoft.AspNetCore.Http.StatusCodes;

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
        public async Task UploadDataset()
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
                        _notifier.Show(apiResponse.Message + " : " + apiResponse.StatusCode, ViewNotifierType.Error, _l["Operation Failed"]);
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
    }
}
