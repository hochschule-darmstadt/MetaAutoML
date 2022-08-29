using BlazorBoilerplate.Infrastructure.Server.Models;
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
        Task<ApiResponse> GetTraining(GetTrainingRequestDto training);
        Task<ApiResponse> GetTrainingIds(GetTrainingIdsRequestDto training);
        Task<ApiResponse> GetAllTrainings(GetAllTrainingsRequestDto training);
        Task<ApiResponse> DeleteTraining(DeleteTrainingRequestDto request);
    }
}
