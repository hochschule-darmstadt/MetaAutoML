using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.PredictionDataset;
using BlazorBoilerplate.Storage;
using Microsoft.Extensions.Caching.Distributed;
using Newtonsoft.Json;
using System.Net;
using System.Text;
using static Microsoft.AspNetCore.Http.StatusCodes;
using static MudBlazor.CategoryTypes;

namespace BlazorBoilerplate.Server.Managers
{
    public class PredictionDatasetManager : IPredictionDatasetManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ILogger<EmailManager> _logger;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public PredictionDatasetManager(ApplicationDbContext dbContext, ILogger<EmailManager> logger, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _logger = logger;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }

        async public Task<ApiResponse> DeletePredictionDataset(DeletePredictionDatasetRequestDto request)
        {
            DeletePredictionDatasetRequest deleteDatasetsRequest = new DeletePredictionDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                deleteDatasetsRequest.PredictionDatasetIdentifier = request.PredictionDatasetIdentifier;
                deleteDatasetsRequest.UserIdentifier = username;
                var reply = _client.DeletePredictionDataset(deleteDatasetsRequest);
                return new ApiResponse(Status200OK, null, "");

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        async public Task<ApiResponse> GetPredictionDatasetPrediction(GetPredictionDatasetPredictionRequestDto request)
        {
            GetPredictionDatasetPredictionResponseDto response = new GetPredictionDatasetPredictionResponseDto();
            GetPredictionDatasetRequest getPredictionDatasetRequest = new GetPredictionDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getPredictionDatasetRequest.UserIdentifier = username;
                getPredictionDatasetRequest.PredictionDatasetIdentifier = request.PredictionDatasetIdentifier;
                var reply = _client.GetPredictionDataset(getPredictionDatasetRequest);

                var predictionPath = reply.PredictionDataset.Predictions[request.ModelIdentifier].Predictions[request.PredictionIdentifier].PredictionPath;
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

        async public Task<ApiResponse> GetPredictionDataset(GetPredictionDatasetRequestDto request)
        {
            GetPredictionDatasetResponseDto response;
            GetPredictionDatasetRequest getDatasetRequest = new GetPredictionDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetRequest.UserIdentifier = username;
                getDatasetRequest.PredictionDatasetIdentifier = request.PredictionDatasetIdentifier;
                var reply = _client.GetPredictionDataset(getDatasetRequest);
                response = new GetPredictionDatasetResponseDto(new PredictionDatasetDto(reply, await _cacheManager.GetObjectInformation(reply.PredictionDataset.Type)));

                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        async public Task<ApiResponse> GetPredictionDatasets(GetPredictionDatasetsRequestDto request)
        {
            GetPredictionDatasetsResponseDto response = new GetPredictionDatasetsResponseDto();
            GetPredictionDatasetsRequest getDatasetsRequest = new GetPredictionDatasetsRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetsRequest.DatasetIdentifier = request.DatasetIdentifier;
                getDatasetsRequest.UserIdentifier = username;
                var reply = _client.GetPredictionDatasets(getDatasetsRequest);
                foreach (PredictionDataset item in reply.PredictionDatasets)
                {
                    response.Datasets.Add(new PredictionDatasetDto(item, await _cacheManager.GetObjectInformation(item.Type)));
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        async public Task<ApiResponse> UploadPredictionDataset(UploadPredictionDatasetRequestDto request)
        {
            CreatePredictionDatasetRequest grpcRequest = new CreatePredictionDatasetRequest();
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
                    grpcRequest.UserIdentifier = username;
                    grpcRequest.FileName = trustedFileNameForDisplay;
                    grpcRequest.PredictionDatasetName = request.PredictionDatasetName;

                    grpcRequest.DatasetIdentifier = request.DatasetIdentifier;
                    var reply = _client.CreatePredictionDataset(grpcRequest);
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
