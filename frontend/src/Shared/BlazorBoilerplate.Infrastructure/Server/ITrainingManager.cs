using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Training;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface ITrainingManager
    {
        Task<ApiResponse> CreateTraining(CreateTrainingRequestDto request);
        Task<ApiResponse> GetTrainingsMetadata(GetTrainingsMetadataRequestDto request);
        Task<ApiResponse> GetTrainingMetadata(GetTrainingMetadataRequestDto request);
        Task<ApiResponse> GetTraining(GetTrainingRequestDto request);
        Task<ApiResponse> DeleteTraining(DeleteTrainingRequestDto request);
        Task<ApiResponse> GetTrainingRuntimeSuggestion(GetTrainingSuggestedRuntimeRequestDto request);
    }
}
