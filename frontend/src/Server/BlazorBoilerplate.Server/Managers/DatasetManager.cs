using Azure;
using BlazorBoilerplate.Constants;
using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Storage;
using Grpc.Core;
using Grpc.Net.Client;
using Microsoft.AspNetCore.Http;
using Microsoft.Data.Analysis;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Serilog.Core;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using static Microsoft.AspNetCore.Http.StatusCodes;
using System.IO.Compression;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls related to datasets
    /// </summary>
    public class DatasetManager : IDatasetManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ILogger<EmailManager> _logger;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public DatasetManager(ApplicationDbContext dbContext, ILogger<EmailManager> logger, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _logger = logger;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }
        /// <summary>
        /// Upload a new dataset, currently only CSV are supported
        /// </summary>
        /// <param name="request"></param>
        /// <returns></returns>
        public async Task<ApiResponse> UploadDataset(UploadDatasetRequestDto request)
        {
            CreateDatasetRequest grpcRequest = new CreateDatasetRequest();
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

                bool correctStrukture = CheckUploadStructure(fs, path);

                if (correctStrukture == true) { 
                //We uploaded everything, send grpc request to controller to persist
                    if (request.ChunkNumber == request.TotalChunkNumber)
                    {
                        fs.Dispose();
                        grpcRequest.UserId = username;
                        grpcRequest.FileName = trustedFileNameForDisplay;
                        grpcRequest.DatasetName = request.DatasetName;

                        grpcRequest.DatasetType = request.DatasetType;
                        var reply = _client.CreateDataset(grpcRequest);
                        return new ApiResponse(Status200OK, null, "");
                    }
                    return new ApiResponse(Status200OK, null, 0);
                }
                else
                {
                    // do not upload data, display a banner that the format is wrong
                    return new ApiResponse(Status406NotAcceptable, null, 0);
                }
            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Get a list of all Datasets
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> GetDatasets()
        {
            GetDatasetsResponseDto response = new GetDatasetsResponseDto();
            GetDatasetsRequest getDatasetsRequest = new GetDatasetsRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetsRequest.Type = "";
                getDatasetsRequest.UserId = username;
                var reply = _client.GetDatasets(getDatasetsRequest);
                foreach (Dataset item in reply.Datasets)
                {
                    response.Datasets.Add(new DatasetDto(item, await _cacheManager.GetObjectInformation(item.Type)));
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        /// <summary>
        /// Retrive a concrete Dataset
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetDataset(GetDatasetRequestDto request)
        {
            GetDatasetResponseDto response;
            GetDatasetRequest getDatasetRequest = new GetDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetRequest.UserId = username;
                getDatasetRequest.DatasetId = request.DatasetId;
                var reply = _client.GetDataset(getDatasetRequest);
                response = new GetDatasetResponseDto(new DatasetDto(reply, await _cacheManager.GetObjectInformation(reply.Dataset.Type)));

                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        /// <summary>
        /// Get a list of all Datasets
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> GetDatasetPreview(GetDatasetPreviewRequestDto request)
        {
            GetDatasetPreviewResponseDto response = new GetDatasetPreviewResponseDto();
            GetDatasetRequest getDatasetRequest = new GetDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
            try
            {
                getDatasetRequest.UserId = username;
                getDatasetRequest.DatasetId = request.DatasetId;
                var reply = _client.GetDataset(getDatasetRequest);
                string datasetLocation = reply.Dataset.Path;
                switch (reply.Dataset.Type)
                {
                    case ":tabular":
                        response.DatasetPreview = File.ReadAllText(datasetLocation.Replace(".csv", "_preview.csv"));

                        break;
                    case ":image":
                        datasetLocation = datasetLocation.Replace(".zip", "");
                        string[] classificationTargets = Directory.GetDirectories(Path.Combine(datasetLocation, "train"));
                        response.DatasetPreview = new List<ImagePreviewDto>();
                        foreach (string classificationTarget in classificationTargets)
                        {
                            for (int i = 0; i < 5; i++)
                            {
                                ImagePreviewDto preview = new ImagePreviewDto();
                                var imgeInfo = GetRandomImage(classificationTarget);
                                preview.FileType = imgeInfo.Item2;
                                preview.FolderType = classificationTarget.Replace(Path.Combine(datasetLocation, "train"), "");
                                preview.Content = GetImageAsBytes(imgeInfo.Item1);
                                response.DatasetPreview.Add(preview);
                            }
                        }
                        break;
                    case ":text":
                        response.DatasetPreview = File.ReadAllText(datasetLocation.Replace(".csv", "_preview.csv"));
                        break;
                    case ":time_series":
                        response.DatasetPreview = File.ReadAllText(datasetLocation.Replace(".csv", "_preview.csv"));
                        break;
                    case ":time_series_longitudinal":
                        response.DatasetPreview = File.ReadAllText(datasetLocation.Replace(".ts", "_preview.csv"));
                        break;
                    default:
                        break;
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                Console.WriteLine(ex.Message);
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Helper function, get all column names of a structured data dataset
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto request)
        {
            GetTabularDatasetColumnResponseDto response = new GetTabularDatasetColumnResponseDto();
            GetTabularDatasetColumnRequest getColumnNamesRequest = new GetTabularDatasetColumnRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getColumnNamesRequest.UserId = username;
                getColumnNamesRequest.DatasetId = request.DatasetId;
                var reply = _client.GetTabularDatasetColumn(getColumnNamesRequest);
                foreach (var item in reply.Columns.ToList())
                {
                    response.Columns.Add(new ColumnsDto
                    {
                        Name = item.Name,
                        Type = item.Type,
                        ConvertibleTypes = item.ConvertibleTypes.ToList(),
                    });
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto request)
        {
            SetDatasetFileConfigurationRequest grpcRequest = new SetDatasetFileConfigurationRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                grpcRequest.UserId = username;
                grpcRequest.DatasetId = request.DatasetId;
                grpcRequest.FileConfiguration = JsonConvert.SerializeObject(request.Configuration);
                var reply = _client.SetDatasetFileConfiguration(grpcRequest);
                return new ApiResponse(Status200OK, null, "");

            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetDatasetAnalysis(GetDatasetAnalysisRequestDto request)
        {
            GetDatasetAnalysisResponseDto response = new GetDatasetAnalysisResponseDto();
            GetDatasetRequest getDatasetRequest = new GetDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
            try
            {
                getDatasetRequest.UserId = username;
                getDatasetRequest.DatasetId = request.DatasetId;
                var reply = _client.GetDataset(getDatasetRequest);
                var analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.Dataset.Analysis);
                int index = 0;
                if (analysis != null)
                {
                    if (analysis.Count != 0)
                    {
                        if (analysis["plots"] != null)
                        {
                            foreach (var category in analysis["plots"])
                            {
                                DatasetAnalysisCategory datasetAnalysisCategory = new DatasetAnalysisCategory()
                                {
                                    CategoryTitle = category.SelectToken("title")
                                };
                                foreach (var item in category["items"])
                                {
                                    if (request.GetShortPreview == true && index++ == 3)
                                    {
                                        break;
                                    }
                                    DatasetAnalysis datasetAnalysis = new DatasetAnalysis()
                                    {
                                        Title = item.SelectToken("title").ToString(),
                                        Type = item.SelectToken("type").ToString(),
                                        Description = item.SelectToken("description").ToString(),
                                        Content = GetImageAsBytes(item.SelectToken("path").ToString())
                                    };
                                    datasetAnalysisCategory.Analyses.Add(datasetAnalysis);
                                }
                                response.AnalysisCategories.Add(datasetAnalysisCategory);
                            }
                        }
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

        private bool CheckUploadStructure(FileStream fs, string path)
        {
            string fileExt = System.IO.Path.GetExtension(fs.Name);
            bool structureCorrect = false;

            // simplify with fs.Name

            if (fileExt == ".csv")
            {
                // .csv does not need validation
                structureCorrect = true; ;
            }
            else if (fileExt == ".zip")
            {
                string extractionLocation = path + "/" + Path.GetFileNameWithoutExtension(fs.Name);
                ZipFile.ExtractToDirectory(fs.Name, extractionLocation);
                if (File.Exists(extractionLocation + "/train") && File.Exists(extractionLocation + "/test"))
                {
                    structureCorrect = true;
                } else
                {
                    structureCorrect = false;
                }
                //Directory.Delete(extractionLocation, true);
            }
            return structureCorrect;
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

        private Tuple<string, string> GetRandomImage(string folder)
        {
            string filename = null;
            string type = null;
            if (!string.IsNullOrEmpty(folder))
            {
                var extensions = new string[] { ".jpeg" };
                try
                {
                    var di = new DirectoryInfo(folder);
                    var randomImage = di.GetFiles("*.*").Where(f => extensions.Contains(f.Extension.ToLower()));
                    Random R = new Random();
                    int index = R.Next(0, randomImage.Count());
                    filename = randomImage.ElementAt(index).FullName;
                    type = randomImage.ElementAt(index).Extension;
                }
                catch (Exception)
                {

                    throw;
                }
            }
            return Tuple.Create(filename, type);
        }

        /// <summary>
        /// Delete a dataset
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> DeleteDataset(DeleteDatasetRequestDto request)
        {
            DeleteDatasetRequest deleteDatasetsRequest = new DeleteDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                deleteDatasetsRequest.DatasetId = request.DatasetId;
                deleteDatasetsRequest.UserId = username;
                var reply = _client.DeleteDataset(deleteDatasetsRequest);
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
