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
        Task<ApiResponse> CreateTraining(CreateTrainingRequestDto request);
        Task<ApiResponse> GetTrainings();
        Task<ApiResponse> GetTraining(GetTrainingRequestDto request);
        Task<ApiResponse> DeleteTraining(DeleteTrainingRequestDto request);
    }
}
