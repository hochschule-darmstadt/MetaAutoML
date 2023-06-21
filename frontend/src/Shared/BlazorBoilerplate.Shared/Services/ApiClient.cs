using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Db;
using BlazorBoilerplate.Shared.Dto.Email;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.Prediction;
using BlazorBoilerplate.Shared.Dto.Training;
using BlazorBoilerplate.Shared.Extensions;
using BlazorBoilerplate.Shared.Interfaces;
using BlazorBoilerplate.Shared.Models;
using Breeze.Sharp;
using Microsoft.Extensions.Logging;
using System.Linq.Expressions;

namespace BlazorBoilerplate.Shared.Services
{
    public class ApiClient : BaseApiClient, IApiClient
    {
        public ApiClient(HttpClient httpClient, ILogger<ApiClient> logger) : base(httpClient, logger)
        { }
        public async Task<UserProfile> GetUserProfile()
        {
            return (await entityManager.ExecuteQuery(new EntityQuery<UserProfile>().From("UserProfile"), CancellationToken.None)).SingleOrDefault();
        }
        public async Task<QueryResult<TenantSetting>> GetTenantSettings()
        {
            return await GetItems<TenantSetting>(from: "TenantSettings", orderBy: i => i.Key);
        }

        public async Task<QueryResult<ApplicationUser>> GetUsers(Expression<Func<ApplicationUser, bool>> predicate = null, int? take = null, int? skip = null)
        {
            return await GetItems("Users", predicate, i => i.UserName, null, take, skip);
        }
        public async Task<QueryResult<ApplicationRole>> GetRoles(Expression<Func<ApplicationRole, bool>> predicate = null, int? take = null, int? skip = null)
        {
            return await GetItems("Roles", predicate, i => i.Name, null, take, skip);
        }

        public async Task<QueryResult<DbLog>> GetLogs(Expression<Func<DbLog, bool>> predicate = null, int? take = null, int? skip = null)
        {
            return await GetItems("Logs", predicate, null, i => i.TimeStamp, take, skip);
        }

        public async Task<QueryResult<ApiLogItem>> GetApiLogs(Expression<Func<ApiLogItem, bool>> predicate = null, int? take = null, int? skip = null)
        {
            return await GetItems("ApiLogs", predicate, null, i => i.RequestTime, take, skip);
        }
        public async Task<QueryResult<Todo>> GetToDos(ToDoFilter filter, int? take = null, int? skip = null)
        {
            return await GetItems<Todo>(from: "Todos", orderByDescending: i => i.CreatedOn, take: take, skip: skip, parameters: filter?.ToDictionary());
        }
        public async Task<QueryResult<ApplicationUser>> GetTodoCreators(ToDoFilter filter)
        {
            return await GetItems<ApplicationUser>(from: "TodoCreators", orderBy: i => i.UserName, parameters: filter?.ToDictionary());
        }
        public async Task<QueryResult<ApplicationUser>> GetTodoEditors(ToDoFilter filter)
        {
            return await GetItems<ApplicationUser>(from: "TodoEditors", orderBy: i => i.UserName, parameters: filter?.ToDictionary());
        }
        public async Task<ApiResponseDto> SendTestEmail(EmailDto email)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Email/SendTestEmail", email);
        }

        #region OMA-ML USER MESSAGES
        public async Task<ApiResponseDto> GetHomeOverviewInformation()
        {
            return await httpClient.GetJsonAsync<ApiResponseDto>("api/User/GetHomeOverviewInformations");
        }
        #endregion

        #region OMA-ML DATASET MESSAGES
        public async Task<ApiResponseDto> UploadDataset(UploadDatasetRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/UploadDataset", request);
        }
        public async Task<ApiResponseDto> GetDatasets()
        {
            return await httpClient.GetJsonAsync<ApiResponseDto>("api/Dataset/GetDatasets");
        }
        public async Task<ApiResponseDto> GetDataset(GetDatasetRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/GetDataset", request);
        }
        public async Task<ApiResponseDto> GetDatasetPreview(GetDatasetPreviewRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/GetDatasetPreview", request);
        }
        public async Task<ApiResponseDto> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/SetDatasetFileConfiguration", request);
        }

        public async Task<ApiResponseDto> SetDatasetColumnSchemaConfiguration(SetDatasetColumnSchemaConfigurationRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/SetDatasetColumnSchemaConfiguration", request);
        }
        public async Task<ApiResponseDto> GetDatasetAnalysis(GetDatasetAnalysisRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/GetDatasetAnalysis", request);
        }
        public async Task<ApiResponseDto> DeleteDataset(DeleteDatasetRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Dataset/DeleteDataset", request);
        }
        #endregion

        #region OMA-ML TRAINING MESSAGES
        public async Task<ApiResponseDto> CreateTraining(CreateTrainingRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Training/CreateTraining", request);
        }
        public async Task<ApiResponseDto> GetTrainings()
        {
            return await httpClient.GetJsonAsync<ApiResponseDto>("api/Training/GetTrainings");
        }
        public async Task<ApiResponseDto> GetTraining(GetTrainingRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Training/GetTraining", request);
        }
        public async Task<ApiResponseDto> DeleteTraining(DeleteTrainingRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Training/DeleteTraining", request);
        }
        #endregion

        #region OMA-ML MODEL MESSAGES

        public async Task<ApiResponseDto> GetModels(GetModelsRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/GetModels", request);
        }
        public async Task<ApiResponseDto> GetModel(GetModelRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/GetModel", request);
        }
        public async Task<ApiResponseDto> GetModelExplanation(GetModelExplanationRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/GetModelExplanation", request);
        }
        public async Task<ApiResponseDto> ModelPrediction(ModelPredictionRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/ModelPrediction", request);
        }
        public async Task<ApiResponseDto> DownloadModel(DownloadModelRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/DownloadModel", request);
        }
        public async Task<ApiResponseDto> DeleteModel(DeleteModelRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/DeleteModel", request);
        }

        public async Task<ApiResponseDto> StartExplainerDashboard(StartDashboardRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Model/StartExplainerDashboard", request);

        }

        #endregion

        #region OMA-ML ONTOLOGY MESSAGES
        public Task<ApiResponseDto<GetAutoMlSolutionsForConfigurationResponseDto>> GetAutoMlSolutionsForConfiguration(GetAutoMlSolutionsForConfigurationRequestDto request)
        {
            return httpClient.PostJsonAsync<ApiResponseDto<GetAutoMlSolutionsForConfigurationResponseDto>>("api/Ontology/GetAutoMlSolutionsForConfiguration", request);
        }
        public Task<ApiResponseDto<GetTasksForDatasetTypeResponseDto>> GetTasksForDatasetType(GetTasksForDatasetTypeRequestDto request)
        {
            return httpClient.PostJsonAsync<ApiResponseDto<GetTasksForDatasetTypeResponseDto>>("api/Ontology/GetTasksForDatasetType", request);
        }
        public async Task<ApiResponseDto> GetDatasetTypes()
        {
            return await httpClient.GetJsonAsync<ApiResponseDto>("api/Ontology/GetDatasetTypes");
        }

        public Task<ApiResponseDto<GetMlLibrariesForTaskResponseDto>> GetMlLibrariesForTask(GetMlLibrariesForTaskRequestDto request)
        {
            return httpClient.PostJsonAsync<ApiResponseDto<GetMlLibrariesForTaskResponseDto>>("api/Ontology/GetMlLibrariesForTask", request);
        }

        public Task<ApiResponseDto<GetAvailableStrategiesResponseDto>> GetAvailableStrategies(GetAvailableStrategiesRequestDto request)
        {
            return httpClient.PostJsonAsync<ApiResponseDto<GetAvailableStrategiesResponseDto>>("api/Ontology/GetAvailableStrategies", request);
        }

        public Task<ApiResponseDto<GetAutoMlParametersResponseDto>> GetAutoMlParameters(GetAutoMlParametersRequestDto request)
        {
            return httpClient.PostJsonAsync<ApiResponseDto<GetAutoMlParametersResponseDto>>("api/Ontology/GetAutoMlParameters", request);
        }
        #endregion

        #region OMA-ML PREDICTION DATASET MESSAGES
        async public Task<ApiResponseDto> UploadPrediction(UploadPredictionRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Prediction/UploadPrediction", request);
        }

        async public Task<ApiResponseDto> GetPrediction(GetPredictionRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Prediction/GetPrediction", request);
        }
        async public Task<ApiResponseDto> GetPredictions(GetPredictionsRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Prediction/GetPredictions", request);
        }

        async public Task<ApiResponseDto> DownloadPrediction(DownloadPredictionRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Prediction/DownloadPrediction", request);
        }

        async public Task<ApiResponseDto> DeletePrediction(DeletePredictionRequestDto request)
        {
            return await httpClient.PostJsonAsync<ApiResponseDto>("api/Prediction/DeletePrediction", request);
        }
        #endregion

    }
}
