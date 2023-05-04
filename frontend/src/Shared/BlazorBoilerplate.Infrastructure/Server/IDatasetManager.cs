using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IDatasetManager
    {
        Task<ApiResponse> UploadDataset(UploadDatasetRequestDto file);
        Task<ApiResponse> GetDatasets();
        Task<ApiResponse> GetDataset(GetDatasetRequestDto dataset);
        Task<ApiResponse> GetDatasetPreview(GetDatasetPreviewRequestDto dataset);
        Task<ApiResponse> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto dataset);
        Task<ApiResponse> SetDatasetColumnSchemaConfiguration(SetDatasetColumnSchemaConfigurationRequestDto dataset);
        Task<ApiResponse> GetDatasetAnalysis(GetDatasetAnalysisRequestDto dataset);
        Task<ApiResponse> DeleteDataset(DeleteDatasetRequestDto request);
    }
}
