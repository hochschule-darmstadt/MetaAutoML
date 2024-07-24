using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Prediction;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.SignalR.Client;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IFileUploader
    {
        Task UploadDatasetFromDisk();
        Task UploadDatasetFromURL(string url, string fileType);
        Task InitHub();
        //UploadDatasetRequestDto UploadDatasetRequest { get; set; }
        UploadDatasetRequestDto UploadDatasetRequest { get; set; }
        UploadPredictionRequestDto UploadPredictionRequest { get; set; }
        IBrowserFile UploadFileContent { get; set; }
        bool IsUploading { get; set; }
        double Progress {  get; set; }
        string UploadText { get; set; }
        Action OnUploadChangedCallback { get; set; }
        Action OnStateHasChangedCallback { get; set; }
        Action RefreshUploadComponentCallback { get; set; }
        Func<Task> OnUploadCompletedCallback { get; set; }
        bool IsUploadDatasetDialogOpen { get; set; }
        bool IsUploadPredictionDatasetDialogOpen { get; set; }
        bool IsPredictionDatasetToUpload { get; set; }
        string SignalRUploadFromDiskConnectionId { get; set; }
        string SignalRUploadFromUrlConnectionId { get; set; }

    }
}
