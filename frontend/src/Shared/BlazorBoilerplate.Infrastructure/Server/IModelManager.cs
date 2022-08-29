using BlazorBoilerplate.Infrastructure.Server.Models;
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
        Task<ApiResponse> GetModel(GetModelRequestDto model);
        Task<ApiResponse> GetModels(GetModelsRequestDto models);
        Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto model);
        Task<ApiResponse> GetModelDownload(GetAutoMlModelRequestDto autoMl);
        Task<ApiResponse> DeleteModel(DeleteModelRequestDto request);
    }
}
