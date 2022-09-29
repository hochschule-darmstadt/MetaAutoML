using BlazorBoilerplate.Shared.Dto.Dataset;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Forms;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IFileUploader
    {
        Task UploadDataset();
        UploadDatasetRequestDto UploadFile { get; set; }
        IBrowserFile UploadFileContent { get; set; }
        bool IsUploading { get; set; }
        Action OnUploadChangedCallback { get; set; }
        Action RefreshUploadComponentCallback { get; set; }
        Func<Task> OnUploadCompletedCallback { get; set; }
        bool IsUploadDialogOpen { get; set; }
    }
}
