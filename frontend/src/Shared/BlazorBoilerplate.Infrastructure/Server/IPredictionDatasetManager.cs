using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.PredictionDataset;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IPredictionDatasetManager
    {
        Task<ApiResponse> UploadPredictionDataset(UploadPredictionDatasetRequestDto request);
        Task<ApiResponse> GetPredictionDatasets(GetPredictionDatasetsRequestDto request);
        Task<ApiResponse> GetPredictionDatasetPrediction(GetPredictionDatasetPredictionRequestDto request);
        Task<ApiResponse> GetPredictionDataset(GetPredictionDatasetRequestDto request);
        Task<ApiResponse> DeletePredictionDataset(DeletePredictionDatasetRequestDto request);
    }
}