using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Prediction;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IPredictionManager
    {
        Task<ApiResponse> UploadPrediction(UploadPredictionRequestDto request);
        Task<ApiResponse> GetPredictions(GetPredictionsRequestDto request);
        Task<ApiResponse> GetPrediction(GetPredictionRequestDto request);
        Task<ApiResponse> DownloadPrediction(DownloadPredictionRequestDto request);
        Task<ApiResponse> DeletePrediction(DeletePredictionRequestDto request);
    }
}