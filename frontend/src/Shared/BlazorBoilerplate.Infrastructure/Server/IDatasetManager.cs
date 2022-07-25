using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IDatasetManager
    {
        Task<ApiResponse> GetDatasetTypes();
        Task<ApiResponse> GetDataset(GetDatasetRequestDto dataset);
        Task<ApiResponse> GetDatasets();
        Task<ApiResponse> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto dataset);
        Task<ApiResponse> Upload(FileUploadRequestDto file);
    }
}
