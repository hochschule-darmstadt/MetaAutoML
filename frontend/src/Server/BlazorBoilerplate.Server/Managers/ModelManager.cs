﻿using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
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
                    ModelDto modelDto = new ModelDto(model, await _cacheManager.GetObjectInformation(model.MlModelType), await _cacheManager.GetObjectInformation(model.MlLibrary), await _cacheManager.GetObjectInformation(model.AutoMlSolution));
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

                response.Model = new ModelDto(reply.Model, await _cacheManager.GetObjectInformation(reply.Model.MlModelType), await _cacheManager.GetObjectInformation(reply.Model.MlLibrary), await _cacheManager.GetObjectInformation(reply.Model.AutoMlSolution));
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto request)
        {
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
                            ModelExplanation modelExplanation = new ModelExplanation()
                            {
                                Title = item.SelectToken("title").ToString(),
                                Type = item.SelectToken("type").ToString(),
                                Description = item.SelectToken("description").ToString(),
                                Content = GetImageAsBytes(item.SelectToken("path").ToString())
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
        /// Get the result model from a specific AutoML
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        public async Task<ApiResponse> DownloadModel(DownloadModelRequestDto request)
        {
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
                byte[] resultFile = File.ReadAllBytes(resultPath);
                response.Content = resultFile;
                response.Name = Path.GetFileName(resultPath);
                return new ApiResponse(Status200OK, null, response);

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
    }
}
