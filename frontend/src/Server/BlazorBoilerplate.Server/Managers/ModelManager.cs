using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Storage;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    public class ModelManager : IModelManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public ModelManager(ApplicationDbContext dbContext, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }
        public async Task<ApiResponse> GetModel(GetModelRequestDto model)
        {
            GetModelResponseDto response = new GetModelResponseDto();
            GetModelRequest getmodelRequest = new GetModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.Username = username;
                getmodelRequest.ModelId = model.ModelId;
                var reply = _client.GetModel(getmodelRequest);

                response.Model = new ModelDto();
                response.Model.ID = reply.Model.Identifier;
                response.Model.Messages = reply.Model.StatusMessages.ToList();
                response.Model.Status = reply.Model.Status;
                response.Model.Name = (await _cacheManager.GetObjectInformation(reply.Model.Automl)).Properties["skos:prefLabel"];
                response.Model.Library = reply.Model.Library;
                response.Model.Model = reply.Model.Model;
                response.Model.TestScore = (double)reply.Model.TestScore;
                response.Model.ValidationScore = (double)reply.Model.ValidationScore;
                response.Model.Predictiontime = (double)reply.Model.PredictionTime;
                response.Model.Runtime = (int)reply.Model.Runtime;
                response.Model.DatasetId = reply.Model.DatasetId;
                response.Model.TrainingId = reply.Model.TrainingId;

                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetModels(GetModelsRequestDto models)
        {
            GetModelsResponseDto response = new GetModelsResponseDto();
            GetModelsRequest getmodelRequest = new GetModelsRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.Username = username;
                getmodelRequest.Top3 = models.Top3Only;
                getmodelRequest.DatasetId = models.DatasetIdentifier;
                var reply = _client.GetModels(getmodelRequest);

                foreach (var item in reply.Models)
                {
                    ModelDto model = new ModelDto();
                    model.ID = item.Identifier;
                    model.Messages = item.StatusMessages.ToList();
                    model.Status = item.Status;
                    model.Name = (await _cacheManager.GetObjectInformation(item.Automl)).Properties["skos:prefLabel"];
                    model.Library = item.Library;
                    model.Model = item.Model;
                    model.TestScore = (double)item.TestScore;
                    model.ValidationScore = (double)item.ValidationScore;
                    model.Predictiontime = (double)item.PredictionTime;
                    model.Runtime = (int)item.Runtime;
                    model.DatasetId = item.DatasetId;
                    model.TrainingId = item.TrainingId;
                    response.Models.Add(model);
                }

                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Get the result model from a specific AutoML
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetModelDownload(GetAutoMlModelRequestDto autoMl)
        {
            GetAutoMlModelResponseDto response = new GetAutoMlModelResponseDto();
            GetAutoMlModelRequest getmodelRequest = new GetAutoMlModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.Username = username;
                getmodelRequest.TrainingId = autoMl.TrainingId;
                getmodelRequest.AutoMl = autoMl.AutoMl;
                var reply = _client.GetAutoMlModel(getmodelRequest);
                response.Name = reply.Name;
                response.Content = reply.File.ToByteArray();
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
