using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Storage;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using static Microsoft.AspNetCore.Http.StatusCodes;
using static MudBlazor.CategoryTypes;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages functionality that access the Model objects
    /// </summary>
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
        public async Task<ApiResponse> GetModels(GetModelsRequestDto request)
        {
            GetModelsResponseDto response = new GetModelsResponseDto();
            GetModelsRequest getmodelRequest = new GetModelsRequest();
            int top3Counter = 0;
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.UserId = username;
                getmodelRequest.DatasetId = request.DatasetId;
                var reply = _client.GetModels(getmodelRequest);

                foreach (var model in reply.Models)
                {
                    if ((request.Top3 == true) && (top3Counter == 3))
                    {
                        break;
                    }
                    List<Metric> metrics = new List<Metric>();
                    foreach (var metric in JObject.Parse(model.TestScore))
                    {
                        metrics.Add(new Metric() { Name = await _cacheManager.GetObjectInformation(metric.Key), Score = (float)metric.Value });

                    }
                    ModelDto modelDto = new ModelDto(model, await _cacheManager.GetObjectInformationList(model.MlModelType.ToList()),
                        await _cacheManager.GetObjectInformationList(model.MlLibrary.ToList()),
                        await _cacheManager.GetObjectInformation(model.AutoMlSolution), metrics);
                    response.Models.Add(modelDto);
                    top3Counter++;
                }

                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetModel(GetModelRequestDto request)
        {
            GetModelResponseDto response = new GetModelResponseDto();
            GetModelRequest getmodelRequest = new GetModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.UserId = username;
                getmodelRequest.ModelId = request.ModelId;
                var reply = _client.GetModel(getmodelRequest);

                List<Metric> metrics = new List<Metric>();
                foreach (var metric in JObject.Parse(reply.Model.TestScore))
                {
                    metrics.Add(new Metric() { Name = await _cacheManager.GetObjectInformation(metric.Key), Score = (float)metric.Value });

                }
                response.Model = new ModelDto(reply.Model, await _cacheManager.GetObjectInformationList(reply.Model.MlModelType.ToList()),
                    await _cacheManager.GetObjectInformationList(reply.Model.MlLibrary.ToList()),
                    await _cacheManager.GetObjectInformation(reply.Model.AutoMlSolution), metrics);
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto request)
        {
            var is_mutagen_setup = Environment.GetEnvironmentVariable("IS_MUTAGEN_SETUP");
            var mutagen_dataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DATASET_FOLDER_PATH");
            var mutagen_docker_ataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DOCKER_DATASET_FOLDER_PATH");
            GetModelExplanationResponseDto response = new GetModelExplanationResponseDto();
            GetModelRequest getModelRequest = new GetModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
            try
            {
                getModelRequest.UserId = username;
                getModelRequest.ModelId = request.ModelId;
                var reply = _client.GetModel(getModelRequest);
                var explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.Model.Explanation);
                int index = 0;
                string graph_path = "";
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
                    foreach (var category in explanation["content"])
                    {
                        ModelExplanationCategory modelExplanationCategory = new ModelExplanationCategory()
                        {
                            CategoryTitle = category.SelectToken("title")
                        };
                        foreach (var item in category["items"])
                        {
                            if (request.GetShortPreview == true)
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
                            graph_path = item.SelectToken("path").ToString();
                            if (is_mutagen_setup == "YES")
                            {
                                graph_path = graph_path.Replace(mutagen_docker_ataset_folder_path, mutagen_dataset_folder_path);
                            }
                            ModelExplanation modelExplanation = new ModelExplanation()
                            {
                                Title = item.SelectToken("title").ToString(),
                                Type = item.SelectToken("type").ToString(),
                                Description = item.SelectToken("description").ToString(),
                                Content = GetImageAsBytes(graph_path)
                            };
                            modelExplanationCategory.Analyses.Add(modelExplanation);
                        }
                        response.AnalysisCategories.Add(modelExplanationCategory);
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
        /// Download a perviously generated ML model
        /// </summary>
        /// <param name="request">The DownloadModelRequestDto providing the model information</param>
        /// <returns>Returns an ApiResponse containing the DownloadModelResponseDto object that holds the ML model</returns>
        public async Task<ApiResponse> DownloadModel(DownloadModelRequestDto request)
        {
            var is_mutagen_setup = Environment.GetEnvironmentVariable("IS_MUTAGEN_SETUP");
            var mutagen_dataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DATASET_FOLDER_PATH");
            var mutagen_docker_ataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DOCKER_DATASET_FOLDER_PATH");
            DownloadModelResponseDto response = new DownloadModelResponseDto();
            GetModelRequest getmodelRequest = new GetModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.UserId = username;
                getmodelRequest.ModelId = request.ModelId;
                var reply = _client.GetModel(getmodelRequest);
                //TODO NEW DOWNLOAD FUNCTIONALITY IMPLEMENTATION

                var resultPath = reply.Model.Path;
                if (is_mutagen_setup == "YES")
                {
                    resultPath = resultPath.Replace(mutagen_docker_ataset_folder_path, mutagen_dataset_folder_path);
                }
                byte[] resultFile = File.ReadAllBytes(resultPath);
                response.Content = resultFile;
                response.Name = Path.GetFileName(resultPath);
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
                deleteModelsRequest.ModelId = request.ModelId;
                deleteModelsRequest.UserId = username;
                var reply = _client.DeleteModel(deleteModelsRequest);
                return new ApiResponse(Status200OK, null, "");

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> StartExplainerDashboard(StartDashboardRequestDto request)
        {
            StartDashboardResponseDto response = new StartDashboardResponseDto();
            StartDashboardRequest startDashboardRequest = new StartDashboardRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                startDashboardRequest.UserId = username;
                startDashboardRequest.ModelId = request.ModelId;
                var reply = _client.StartExplainerDashboard(startDashboardRequest);
                response.Url = reply.Url;
                response.SessionId = reply.SessionId;
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> StopExplainerDashboard(StopDashboardRequestDto request)
        {
            StopDashboardRequestDto response = new StopDashboardRequestDto();
            StopDashboardRequest stopDashboardRequest = new StopDashboardRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                stopDashboardRequest.SessionId = request.SessionId;
                var reply = _client.StopExplainerDashboard(stopDashboardRequest);
                return new ApiResponse(Status200OK, null, "");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
