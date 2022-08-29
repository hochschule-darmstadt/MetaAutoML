using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Storage;
using Newtonsoft.Json;
using static Microsoft.AspNetCore.Http.StatusCodes;
using static MudBlazor.CategoryTypes;

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
                if (!string.IsNullOrEmpty(reply.Model.Model))
                {
                    response.Model.Library = (await _cacheManager.GetObjectInformation(reply.Model.Library)).Properties["skos:prefLabel"];
                    response.Model.Model = (await _cacheManager.GetObjectInformation(reply.Model.Model)).Properties["skos:prefLabel"];
                }
                else
                {
                    response.Model.Library = "";
                    response.Model.Model = "";
                }
                if (!string.IsNullOrEmpty(reply.Model.Explanation))
                {
                    response.Model.Explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.Model.Explanation);
                }
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
        /// <summary>
        /// Delete a model
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> DeleteModel(DeleteModelRequestDto request)
        {
            DeleteModelResponseDto response = new DeleteModelResponseDto();
            DeleteModelRequest deleteModelsRequest = new DeleteModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                deleteModelsRequest.Identifier = request.Identifier;
                deleteModelsRequest.Username = username;
                var reply = _client.DeleteModel(deleteModelsRequest);
                response.Result = (int)reply.Status;
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
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
                    if (!string.IsNullOrEmpty(item.Model))
                    {
                        model.Library = (await _cacheManager.GetObjectInformation(item.Library)).Properties["skos:prefLabel"];
                        model.Model = (await _cacheManager.GetObjectInformation(item.Model)).Properties["skos:prefLabel"];
                    }
                    else
                    {
                        model.Library = "";
                        model.Model = "";
                    }
                    if (!string.IsNullOrEmpty(item.Explanation))
                    {
                        model.Explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(item.Explanation);
                    }
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
        public async Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto model)
        {
            GetModelExplanationResponseDto response = new GetModelExplanationResponseDto();
            GetModelRequest getModelRequest = new GetModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
            try
            {
                getModelRequest.Username = username;
                getModelRequest.ModelId = model.ModelIdentifier;
                var reply = _client.GetModel(getModelRequest);
                var explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.Model.Explanation);
                int index = 0;
                if (explanation == null)
                {
                    response.Status = "";
                    response.Detail = "";
                }
                else if (explanation["status"] == "started")
                {
                    response.Status = explanation["status"];
                    response.Detail = "";
                }
                else
                {
                    response.Status = explanation["status"];
                    response.Detail = explanation["detail"];
                    foreach (var item in explanation["plots"])
                    {
                        if (model.GetShortPreview == true)
                        {
                            if (item.SelectToken("type").ToString() == "force_plot")
                            {
                                continue;
                            }
                            else if (index++ == 3)
                            {
                                break;
                            }
                        }
                        ModelExplanation datasetAnalysis = new ModelExplanation()
                        {
                            Title = item.SelectToken("title").ToString(),
                            Type = item.SelectToken("type").ToString(),
                            Description = item.SelectToken("description").ToString(),
                            Content = GetImageAsBytes(item.SelectToken("path").ToString())
                        };
                        response.Analyses.Add(datasetAnalysis);
                    }
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        private byte[] GetImageAsBytes(string path)
        {
            byte[] content = null;
            FileStream fileStream = new FileStream(path, FileMode.Open, FileAccess.Read);
            using (BinaryReader reader = new BinaryReader(fileStream))
            {
                content = reader.ReadBytes((int)reader.BaseStream.Length);
            }
            return content;
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
