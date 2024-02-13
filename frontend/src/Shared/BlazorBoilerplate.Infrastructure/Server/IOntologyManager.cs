using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IOntologyManager
    {

        Task<ApiResponse> GetAutoMlSolutionsForConfiguration(GetAutoMlSolutionsForConfigurationRequestDto request);
        Task<ApiResponse> GetTasksForDatasetType(GetTasksForDatasetTypeRequestDto request);
        Task<ApiResponse> GetDatasetTypes();
        Task<ApiResponse> GetMlLibrariesForTask(GetMlLibrariesForTaskRequestDto request);
        Task<ApiResponse> GetSearchRelevantData();
        Task<ApiResponse> GetAvailableStrategies(GetAvailableStrategiesRequestDto request);
        Task<ApiResponse> GetAutoMlParameters(GetAutoMlParametersRequestDto request);

    }
}
