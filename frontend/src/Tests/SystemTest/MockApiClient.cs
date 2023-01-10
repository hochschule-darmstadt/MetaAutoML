using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Db;
using BlazorBoilerplate.Shared.Dto.Email;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.Prediction;
using BlazorBoilerplate.Shared.Dto.Training;
using BlazorBoilerplate.Shared.Interfaces;
using BlazorBoilerplate.Shared.Models;
using Breeze.Sharp;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Text;
using System.Threading.Tasks;

namespace SystemTest
{
    internal class MockApiClient : IApiClient
    {
        public event EventHandler<EntityChangedEventArgs> EntityChanged;

        public void AddEntity(IEntity entity)
        {
            throw new NotImplementedException();
        }

        public void CancelChanges()
        {
            throw new NotImplementedException();
        }

        public void ClearEntitiesCache()
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> CreateTraining(CreateTrainingRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> DeleteDataset(DeleteDatasetRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> DeleteModel(DeleteModelRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> DeletePrediction(DeletePredictionRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> DeleteTraining(DeleteTrainingRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> DownloadModel(DownloadModelRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> DownloadPrediction(DownloadPredictionRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<ApiLogItem>> GetApiLogs(Expression<Func<ApiLogItem, bool>> predicate = null, int? take = null, int? skip = null)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetAutoMlSolutionsForConfiguration(GetAutoMlSolutionsForConfigurationRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetAvailableStrategies(GetAvailableStrategiesRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetDataset(GetDatasetRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetDatasetAnalysis(GetDatasetAnalysisRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetDatasetPreview(GetDatasetPreviewRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetDatasets()
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetDatasetTypes()
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetHomeOverviewInformation()
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<T>> GetItems<T>(string from, Expression<Func<T, bool>> predicate = null, Expression<Func<T, object>> orderBy = null, Expression<Func<T, object>> orderByDescending = null, int? take = null, int? skip = null, Dictionary<string, object> parameters = null)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<T>> GetItemsByFilter<T>(string from, string orderByDefaultField, string filter = null, string orderBy = null, string orderByDescending = null, int? take = null, int? skip = null, Dictionary<string, object> parameters = null)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<DbLog>> GetLogs(Expression<Func<DbLog, bool>> predicate = null, int? take = null, int? skip = null)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetMlLibrariesForTask(GetMlLibrariesForTaskRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetModel(GetModelRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetModelExplanation(GetModelExplanationRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetModels(GetModelsRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetPrediction(GetPredictionRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetPredictions(GetPredictionsRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<ApplicationRole>> GetRoles(Expression<Func<ApplicationRole, bool>> predicate = null, int? take = null, int? skip = null)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetTasksForDatasetType(GetTasksForDatasetTypeRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<TenantSetting>> GetTenantSettings()
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<ApplicationUser>> GetTodoCreators(ToDoFilter filter)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<ApplicationUser>> GetTodoEditors(ToDoFilter filter)
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<Todo>> GetToDos(ToDoFilter filter, int? take = null, int? skip = null)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetTraining(GetTrainingRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> GetTrainings()
        {
            throw new NotImplementedException();
        }

        public Task<UserProfile> GetUserProfile()
        {
            throw new NotImplementedException();
        }

        public Task<QueryResult<ApplicationUser>> GetUsers(Expression<Func<ApplicationUser, bool>> predicate = null, int? take = null, int? skip = null)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> ModelPrediction(ModelPredictionRequestDto request)
        {
            throw new NotImplementedException();
        }

        public void RemoveEntity(IEntity entity)
        {
            throw new NotImplementedException();
        }

        public Task SaveChanges()
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> SendTestEmail(EmailDto email)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto request)
        {
            throw new NotImplementedException();
        }

        public Task<ApiResponseDto> UploadDataset(UploadDatasetRequestDto request)
        {
            ApiResponseDto respone = new();
            respone.StatusCode = 200;
            return Task.FromResult(respone);
        }

        public Task<ApiResponseDto> UploadPrediction(UploadPredictionRequestDto request)
        {
            ApiResponseDto respone = new();
            respone.StatusCode = 200;
            return Task.FromResult(respone);
        }
    }
}
