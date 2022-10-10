using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Model;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IModelManager
    {
        Task<ApiResponse> GetModels(GetModelsRequestDto request);
        Task<ApiResponse> GetModel(GetModelRequestDto request);
        Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto request);
        Task<ApiResponse> DownloadModel(DownloadModelRequestDto request);
        Task<ApiResponse> DeleteModel(DeleteModelRequestDto request);
    }
}
