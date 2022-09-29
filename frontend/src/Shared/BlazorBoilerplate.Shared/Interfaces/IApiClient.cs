using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Db;
using BlazorBoilerplate.Shared.Dto.Email;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.Training;
using BlazorBoilerplate.Shared.Models;
using Breeze.Sharp;
using System.Linq.Expressions;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IApiClient : IBaseApiClient
    {
        Task<UserProfile> GetUserProfile();

        Task<QueryResult<TenantSetting>> GetTenantSettings();
        Task<QueryResult<ApplicationUser>> GetUsers(Expression<Func<ApplicationUser, bool>> predicate = null, int? take = null, int? skip = null);
        Task<QueryResult<ApplicationRole>> GetRoles(Expression<Func<ApplicationRole, bool>> predicate = null, int? take = null, int? skip = null);

        Task<QueryResult<DbLog>> GetLogs(Expression<Func<DbLog, bool>> predicate = null, int? take = null, int? skip = null);
        Task<QueryResult<ApiLogItem>> GetApiLogs(Expression<Func<ApiLogItem, bool>> predicate = null, int? take = null, int? skip = null);

        Task<QueryResult<Todo>> GetToDos(ToDoFilter filter, int? take = null, int? skip = null);
        Task<QueryResult<ApplicationUser>> GetTodoCreators(ToDoFilter filter);
        Task<QueryResult<ApplicationUser>> GetTodoEditors(ToDoFilter filter);

        Task<ApiResponseDto> SendTestEmail(EmailDto email);


        #region OMA-ML USER MESSAGES
        Task<ApiResponseDto> GetHomeOverviewInformation();
        #endregion

        #region OMA-ML DATASET MESSAGES
        Task<ApiResponseDto> UploadDatasetFile(MultipartFormDataContent file);
        Task<ApiResponseDto> UploadDataset(FileUploadRequestDto file);
        Task<ApiResponseDto> GetDatasets();
        Task<ApiResponseDto> GetDataset(GetDatasetRequestDto name);
        Task<ApiResponseDto> GetDatasetPreview(GetDatasetPreviewRequestDto dataset);
        Task<ApiResponseDto> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto dataset);
        Task<ApiResponseDto> SetDatasetConfiguration(SetDatasetFileConfigurationRequestDto dataset);
        Task<ApiResponseDto> GetDatasetAnalysis(GetDatasetAnalysisRequestDto dataset);
        Task<ApiResponseDto> DeleteDataset(DeleteDatasetRequestDto request);
        #endregion

        #region OMA-ML TRAINING MESSAGES

        Task<ApiResponseDto> GetTrainings(GetTrainingIdsRequestDto training);
        Task<ApiResponseDto> GetTraining(GetTrainingRequestDto training);
        Task<ApiResponseDto> GetAllTrainings(GetAllTrainingsRequestDto training);
        Task<ApiResponseDto> StartAutoML(StartAutoMLRequestDto automl);
        Task<ApiResponseDto> DeleteTraining(DeleteModelRequestDto request);
        #endregion

        #region OMA-ML MODEL MESSAGES

        Task<ApiResponseDto> GetModels(GetModelsRequestDto models);
        Task<ApiResponseDto> GetModel(GetModelRequestDto model);
        Task<ApiResponseDto> GetModelExplanation(GetModelExplanationRequestDto model);
        Task<ApiResponseDto> GetModelDownload(GetAutoMlModelRequestDto automl);
        Task<ApiResponseDto> TestAutoML(TestAutoMLRequestDto datasetName);
        Task<ApiResponseDto> DeleteModel(DeleteTrainingRequestDto request);

        #endregion

        #region OMA-ML ONTOLOGY MESSAGES
        Task<ApiResponseDto> GetDatasetTypes();
        Task<ApiResponseDto> GetCompatibleAutoMlSolutions(GetCompatibleAutoMlSolutionsRequestDto request);
        Task<ApiResponseDto> GetSupportedMlLibraries(GetSupportedMlLibrariesRequestDto task);
        Task<ApiResponseDto> GetDatasetCompatibleTasks(GetDatasetCompatibleTasksRequestDto dataset);
        Task<ApiResponseDto> GetAvailableStrategies(GetAvailableStrategiesRequestDto request);
        #endregion

    }
}
