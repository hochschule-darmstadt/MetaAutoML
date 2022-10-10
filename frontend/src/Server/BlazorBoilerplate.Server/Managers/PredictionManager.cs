using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.Prediction;
using BlazorBoilerplate.Storage;
using Microsoft.Extensions.Caching.Distributed;
using Newtonsoft.Json;
using System.Net;
using System.Text;
using static Microsoft.AspNetCore.Http.StatusCodes;
using static MudBlazor.CategoryTypes;

namespace BlazorBoilerplate.Server.Managers
{
    public class PredictionManager : IPredictionManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ILogger<EmailManager> _logger;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public PredictionManager(ApplicationDbContext dbContext, ILogger<EmailManager> logger, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _logger = logger;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }

        async public Task<ApiResponse> DeletePrediction(DeletePredictionRequestDto request)
        {
            DeletePredictionRequest deleteDatasetsRequest = new DeletePredictionRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                deleteDatasetsRequest.PredictionId = request.PredictionId;
                deleteDatasetsRequest.UserId = username;
                var reply = _client.DeletePrediction(deleteDatasetsRequest);
                return new ApiResponse(Status200OK, null, "");

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        async public Task<ApiResponse> DownloadPrediction(DownloadPredictionRequestDto request)
        {
            DownloadPredictionResponseDto response = new DownloadPredictionResponseDto();
            GetPredictionRequest getPredictionDatasetRequest = new GetPredictionRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getPredictionDatasetRequest.UserId = username;
                getPredictionDatasetRequest.PredictionId = request.PredictionId;
                var reply = _client.GetPrediction(getPredictionDatasetRequest);

                var predictionPath = reply.Prediction.PredictionPath;
                byte[] predictionFile = File.ReadAllBytes(predictionPath);
                response.Content = predictionFile;
                response.Name = "predicitons.csv";
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }


        async public Task<ApiResponse> GetPrediction(GetPredictionRequestDto request)
        {
            GetPredictionResponseDto response;
            GetPredictionRequest getPredictionDatasetRequest = new GetPredictionRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getPredictionDatasetRequest.UserId = username;
                getPredictionDatasetRequest.PredictionId = request.PredictionId;
                var reply = _client.GetPrediction(getPredictionDatasetRequest);

                response = new GetPredictionResponseDto(reply);

                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        async public Task<ApiResponse> GetPredictions(GetPredictionsRequestDto request)
        {
            GetPredictionsResponseDto response;
            GetPredictionsRequest getPredictionsRequest = new GetPredictionsRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getPredictionsRequest.ModelId = request.ModelId;
                getPredictionsRequest.UserId = username;
                var reply = _client.GetPredictions(getPredictionsRequest);
                response = new GetPredictionsResponseDto(reply);
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        async public Task<ApiResponse> UploadPrediction(UploadPredictionRequestDto request)
        {
            CreatePredictionRequest grpcRequest = new CreatePredictionRequest();
            try
            {
                var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
                string trustedFileNameForDisplay = WebUtility.HtmlEncode(request.FileName);
                string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
                var path = Path.Combine(controllerDatasetPath, username, "uploads");

                if (request.ChunkNumber == 1)
                {
                    var dir = new DirectoryInfo(path);

                    foreach (var info in dir.GetFiles())
                    {
                        info.Delete();
                    }
                }

                if (!Directory.Exists(path))
                {
                    Directory.CreateDirectory(path);
                }

                await using FileStream fs = new(Path.Combine(path, trustedFileNameForDisplay), FileMode.Append);
                fs.Write(request.Content, 0, request.Content.Length);

                //We uploaded everything, send grpc request to controller to persist
                if (request.ChunkNumber == request.TotalChunkNumber)
                {
                    fs.Dispose();
                    grpcRequest.UserId = username;
                    grpcRequest.LiveDatasetFileName = trustedFileNameForDisplay;
                    grpcRequest.ModelId = request.ModelId;

                    var reply = _client.CreatePrediction(grpcRequest);
                    return new ApiResponse(Status200OK, null, "");
                }
                return new ApiResponse(Status200OK, null, 0);
            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
