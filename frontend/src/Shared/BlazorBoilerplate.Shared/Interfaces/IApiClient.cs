using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Db;
using BlazorBoilerplate.Shared.Dto.Email;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.PredictionDataset;
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
        Task<ApiResponseDto> UploadDataset(UploadDatasetRequestDto request);
        Task<ApiResponseDto> GetDatasets();
        Task<ApiResponseDto> GetDataset(GetDatasetRequestDto request);
        Task<ApiResponseDto> GetDatasetPreview(GetDatasetPreviewRequestDto request);
        Task<ApiResponseDto> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto request);
        Task<ApiResponseDto> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto request);
        Task<ApiResponseDto> GetDatasetAnalysis(GetDatasetAnalysisRequestDto request);
        Task<ApiResponseDto> DeleteDataset(DeleteDatasetRequestDto request);
        #endregion

        #region OMA-ML TRAINING MESSAGES
        Task<ApiResponseDto> CreateTraining(CreateTrainingRequestDto request);
        Task<ApiResponseDto> GetTrainings();
        Task<ApiResponseDto> GetTraining(GetTrainingRequestDto request);
        Task<ApiResponseDto> DeleteTraining(DeleteModelRequestDto request);
        #endregion

        #region OMA-ML MODEL MESSAGES

        Task<ApiResponseDto> GetModels(GetModelsRequestDto request);
        Task<ApiResponseDto> GetModel(GetModelRequestDto request);
        Task<ApiResponseDto> GetModelExplanation(GetModelExplanationRequestDto request);
        Task<ApiResponseDto> ModelPrediction(ModelPredictionRequestDto request);
        Task<ApiResponseDto> DownloadModel(DownloadModelRequestDto request);
        Task<ApiResponseDto> DeleteModel(DeleteTrainingRequestDto request);

        #endregion

        #region OMA-ML ONTOLOGY MESSAGES
        Task<ApiResponseDto> GetAutoMlSolutionsForConfiguration(GetAutoMlSolutionsForConfigurationRequestDto request);
        Task<ApiResponseDto> GetTasksForDatasetType(GetTasksForDatasetTypeRequestDto request);
        Task<ApiResponseDto> GetDatasetTypes();
        Task<ApiResponseDto> GetMlLibrariesForTask(GetMlLibrariesForTaskRequestDto request);
        Task<ApiResponseDto> GetAvailableStrategies(GetAvailableStrategiesRequestDto request);
        #endregion

        #region OMA-ML PREDICTION DATASET MESSAGES
        Task<ApiResponseDto> UploadPredictionDataset(UploadPredictionDatasetRequestDto request);
        Task<ApiResponseDto> GetPredictionDatasetPrediction(GetPredictionDatasetPredictionRequestDto request);
        Task<ApiResponseDto> GetPredictionDatasets(GetPredictionDatasetsRequestDto request);
        Task<ApiResponseDto> GetPredictionDataset(GetPredictionDatasetRequestDto request);
        Task<ApiResponseDto> DeletePredictionDataset(DeletePredictionDatasetRequestDto request);
        #endregion

    }
}
