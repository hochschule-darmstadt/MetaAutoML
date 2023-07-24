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
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.Analysis;
using Microsoft.Extensions.Logging;
using MudBlazor.Charts;
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
using UtfUnknown;
using static Microsoft.AspNetCore.Http.StatusCodes;
using System.IO.Compression;
using System.Runtime.CompilerServices;
using Karambolo.Common;
using System.Diagnostics;
using static MudBlazor.CategoryTypes;

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
                string trustedFileNameForDisplay = WebUtility.HtmlEncode(request.FileNameOrURL);
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

                // get the complete file path before fs is released
                string filePath = path + "/" + Path.GetFileName(fs.Name);

                if (request.ChunkNumber == request.TotalChunkNumber)
                {
                    fs.Dispose();

                    grpcRequest.DatasetType = request.DatasetType;
                    DetectionResult result;
                    if (grpcRequest.DatasetType == ":text" || grpcRequest.DatasetType == ":tabular" || grpcRequest.DatasetType == ":time_series" || grpcRequest.DatasetType == ":time_series_longitudinal")
                    {
                        using (FileStream fs1 = new FileStream(Path.Combine(path, trustedFileNameForDisplay), FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                        {
                            result = CharsetDetector.DetectFromStream(fs1);

                        }
                        grpcRequest.Encoding = result.Detected.EncodingName.ToString();
                        //ascii data encoding causes some issues with some automl, UTF-8 is a safe encoding that covers all ascii signs
                        if (grpcRequest.Encoding == "ascii")
                        {
                            grpcRequest.Encoding = "utf-8";
                        }
                    }
                    else
                    {
                        grpcRequest.Encoding = "";
                    }
                    bool correctStrukture = CheckUploadStructure(filePath);

                    if (correctStrukture == true)
                        {
                            grpcRequest.UserId = username;
                            grpcRequest.FileName = trustedFileNameForDisplay;
                            grpcRequest.DatasetName = request.DatasetName;
                            grpcRequest.DatasetType = request.DatasetType;
                            var reply = _client.CreateDataset(grpcRequest);
                            return new ApiResponse(Status200OK, null, "");
                    }
                    else
                    {
                        return new ApiResponse(Status406NotAcceptable, "FolderStructureNotCorrectErrorMessage");
                    }
                }
                return new ApiResponse(Status200OK, null, "");
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
                    Dictionary<string, Shared.Dto.Dataset.ColumnSchemaDto> schema = new Dictionary<string, Shared.Dto.Dataset.ColumnSchemaDto>();
                    foreach (var column in item.Schema)
                    {
                        schema.Add(column.Key, new Shared.Dto.Dataset.ColumnSchemaDto(
                            await _cacheManager.GetObjectInformation(column.Value.DatatypeDetected),
                            await _cacheManager.GetObjectInformationList(column.Value.DatatypesCompatible.ToList()),
                            column.Value.DatatypeSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.DatatypeSelected),
                            await _cacheManager.GetObjectInformationList(column.Value.RolesCompatible.ToList()),
                            column.Value.RoleSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.RoleSelected)));
                    }
                    response.Datasets.Add(new DatasetDto(item, await _cacheManager.GetObjectInformation(item.Type), schema));
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
                Dictionary<string, Shared.Dto.Dataset.ColumnSchemaDto> schema = new Dictionary<string, Shared.Dto.Dataset.ColumnSchemaDto>();
                foreach (var column in reply.Dataset.Schema)
                {
                    schema.Add(column.Key, new Shared.Dto.Dataset.ColumnSchemaDto(
                        await _cacheManager.GetObjectInformation(column.Value.DatatypeDetected),
                        await _cacheManager.GetObjectInformationList(column.Value.DatatypesCompatible.ToList()),
                        column.Value.DatatypeSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.DatatypeSelected),
                        await _cacheManager.GetObjectInformationList(column.Value.RolesCompatible.ToList()),
                        column.Value.RoleSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.RoleSelected)));
                }
                response = new GetDatasetResponseDto(new DatasetDto(reply, await _cacheManager.GetObjectInformation(reply.Dataset.Type), schema));

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
            var is_mutagen_setup = Environment.GetEnvironmentVariable("IS_MUTAGEN_SETUP");
            var mutagen_dataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DATASET_FOLDER_PATH");
            var mutagen_docker_ataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DOCKER_DATASET_FOLDER_PATH");
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
                if (is_mutagen_setup == "YES")
                {
                    datasetLocation = datasetLocation.Replace(mutagen_docker_ataset_folder_path, mutagen_dataset_folder_path);
                }
                switch (reply.Dataset.Type)
                {
                    case ":tabular":
                     
                        response.DatasetPreview = datasetLocation;

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

                        response.DatasetPreview = datasetLocation; 
                        break;
                    case ":time_series":
                      
                        response.DatasetPreview = datasetLocation;
                        break;
                    case ":time_series_longitudinal":
                       
                        response.DatasetPreview = datasetLocation;
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
        public async Task<ApiResponse> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto request)
        {
            SetDatasetConfigurationRequest grpcRequest = new SetDatasetConfigurationRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                grpcRequest.UserId = username;
                grpcRequest.DatasetId = request.DatasetId;
                grpcRequest.FileConfiguration = JsonConvert.SerializeObject(request.Configuration);
                var reply = _client.SetDatasetConfiguration(grpcRequest);
                return new ApiResponse(Status200OK, null, "");

            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> SetDatasetColumnSchemaConfiguration(SetDatasetColumnSchemaConfigurationRequestDto request)
        {
            SetDatasetColumnSchemaConfigurationRequest grpcRequest = new SetDatasetColumnSchemaConfigurationRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                grpcRequest.UserId = username;
                grpcRequest.DatasetId = request.DatasetId;
                grpcRequest.DatatypeSelected = request.SelectedDatatype == null ? "" : request.SelectedDatatype;
                grpcRequest.RoleSelected = request.SelectedRole == null ? "" : request.SelectedRole;
                grpcRequest.Column = request.Column;
                var reply = _client.SetDatasetColumnSchemaConfiguration(grpcRequest);
                return new ApiResponse(Status200OK, null, "");

            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetDatasetAnalysis(GetDatasetAnalysisRequestDto request)
        {
            var is_mutagen_setup = Environment.GetEnvironmentVariable("IS_MUTAGEN_SETUP");
            var mutagen_dataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DATASET_FOLDER_PATH");
            var mutagen_docker_ataset_folder_path = Environment.GetEnvironmentVariable("MUTAGEN_DOCKER_DATASET_FOLDER_PATH");
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
                string graph_path = "";
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
                                    graph_path = item.SelectToken("path").ToString();
                                    if (is_mutagen_setup == "YES")
                                    {
                                        graph_path = graph_path.Replace(mutagen_docker_ataset_folder_path, mutagen_dataset_folder_path);
                                    }
                                    DatasetAnalysis datasetAnalysis = new DatasetAnalysis()
                                    {
                                        Title = item.SelectToken("title").ToString(),
                                        Type = item.SelectToken("type").ToString(),
                                        Description = item.SelectToken("description").ToString(),
                                        Content = GetImageAsBytes(graph_path)
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

        private bool CheckUploadStructure(string filePath)
        {
            string fileExt = filePath.Substring(filePath.Length - 4);
            List<string> zipEntries = new List<string>();

            if (fileExt == ".csv")
            {
                // .csv does not need validation at the moment
                return true; 
            }
            else if (fileExt == ".zip")
            {
                using (ZipArchive archive = ZipFile.OpenRead(filePath))
                {
                    foreach (ZipArchiveEntry entry in archive.Entries)
                    {
                        // take only top level folders, look for test and train
                        if (entry.FullName.EndsWith("/train/") || entry.FullName.EndsWith("/test/"))
                        {
                            zipEntries.Add(entry.FullName);
                        }
                    }
                }
                // if test and train are found, return true
                if (zipEntries.Count == 2)
                {
                    return true;
                }
            }
            return false;
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
