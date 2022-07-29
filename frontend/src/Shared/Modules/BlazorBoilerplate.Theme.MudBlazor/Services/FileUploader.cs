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

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class FileUploader : IFileUploader
    {
        private IApiClient _client;
        private IViewNotifier _notifier;
        private IStringLocalizer<Global> L;
        public FileUploader(IApiClient client, IViewNotifier notifier, IStringLocalizer<Global> L)
        {
            _client = client;
            _notifier = notifier;
            L = L;
        }
        public FileUploadRequestDto UploadFile { get; set; }
        public IBrowserFile UploadFileContent { get; set; }
        public bool IsUploading { get; set; } = false;
        public Action OnUploadChangedCallback { get; set; }
        public Action RefreshUploadComponentCallback { get; set; }
        public bool IsUploadDialogOpen { get; set; } = false;
        public async Task UploadDataset()
        {
            int chunkSize = 100000; 
            int chunkAmount;
            long bytesRead = 0;
            byte[] data = new byte[chunkSize];
            IsUploading = true;
            try
            {
                MemoryStream ms = new MemoryStream();
                var reader = new StreamReader(UploadFileContent.OpenReadStream(long.MaxValue));
                await reader.BaseStream.CopyToAsync(ms);
                ms.Seek(0, SeekOrigin.Begin);
                if ((ms.Length % chunkSize) == 0) //no extra chunk
                {
                    UploadFile.TotalChunkNumber = (int)(ms.Length / chunkSize);
                }
                else
                {
                    UploadFile.TotalChunkNumber = (int)(ms.Length / chunkSize) + 1;      //append extra chunk
                }
                UploadFile.ChunkNumber = 1;
                while (bytesRead < ms.Length)
                {
                    var bytesToRead = ms.Length - bytesRead;
                    var bufferSize = Math.Min(chunkSize, bytesToRead);
                    var buffer = new byte[bufferSize];
                    var reallyRead = ms.Read(buffer, 0, buffer.Length);
                    UploadFile.Content = buffer;

                    ApiResponseDto apiResponse = new ApiResponseDto();
                    apiResponse = await _client.UploadDataset(UploadFile);
                    if (!apiResponse.IsSuccessStatusCode)
                    {
                        _notifier.Show(apiResponse.Message + " : " + apiResponse.StatusCode, ViewNotifierType.Error, L["Operation Failed"]);
                    }

                    bytesRead += reallyRead;
                    UploadFile.ChunkNumber++;
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
            }
            catch (Exception ex)
            {
                _notifier.Show(ex.Message, ViewNotifierType.Error, L["Operation Failed"]);
            }
            return;
        }
    }
}
