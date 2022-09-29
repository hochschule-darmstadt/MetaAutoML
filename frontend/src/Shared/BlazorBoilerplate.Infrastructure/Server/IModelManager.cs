using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Model;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IModelManager
    {
        Task<ApiResponse> GetModels(GetModelsRequestDto request);
        Task<ApiResponse> GetModel(GetModelRequestDto request);
        Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto request);
        Task<ApiResponse> ModelPrediction(ModelPredictRequestDto request);
        Task<ApiResponse> DownloadModel(DownloadModelRequestDto request);
        Task<ApiResponse> DeleteModel(DeleteModelRequestDto request);
    }
}
