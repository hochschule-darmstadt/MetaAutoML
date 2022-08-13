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
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using static Microsoft.AspNetCore.Http.StatusCodes;

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
        /// Retrive all Dataset Types
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> GetDatasetTypes()
        {
            GetDatasetTypesResponseDto response = new GetDatasetTypesResponseDto();
            try
            {
                var reply = _client.GetDatasetTypes(new GetDatasetTypesRequest());
                response.DatasetTypes = await _cacheManager.GetObjectInformationList(reply.DatasetTypes.ToList());
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        /// <summary>
        /// Retrive a concrete Dataset
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetDataset(GetDatasetRequestDto dataset)
        {
            GetDatasetResponseDto response;
            GetDatasetRequest getDatasetRequest = new GetDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetRequest.Username = username;
                getDatasetRequest.Identifier = dataset.Identifier;
                var reply = _client.GetDataset(getDatasetRequest);
                response = new GetDatasetResponseDto();
                response.Name = reply.DatasetInfos.Name;
                response.Type = await _cacheManager.GetObjectInformation(reply.DatasetInfos.Type);
                response.Size = reply.DatasetInfos.Size;
                response.Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.DatasetInfos.Analysis);
                response.Creation_date = reply.DatasetInfos.CreationDate.ToDateTime();
                response.Identifier = reply.DatasetInfos.Identifier;

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
        public async Task<ApiResponse> GetDatasets()
        {
            GetDatasetsResponseDto response = new GetDatasetsResponseDto();
            GetDatasetsRequest getDatasetsRequest = new GetDatasetsRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetsRequest.Type = DatasetType.TabularData;
                getDatasetsRequest.Username = username;
                var reply = _client.GetDatasets(getDatasetsRequest);
                foreach (Dataset item in reply.Dataset)
                {
                    ObjectInfomationDto typeInformation = await _cacheManager.GetObjectInformation(item.Type);
                    response.Datasets.Add(new GetDatasetResponseDto()
                    {
                        Name = item.Name,
                        Type = await _cacheManager.GetObjectInformation(item.Type),
                        Size = item.Size,
                        Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(item.Analysis),
                        Creation_date = item.CreationDate.ToDateTime(),
                        Identifier = item.Identifier
                    });
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
        /// Get a list of all Datasets
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> GetDatasetPreview(GetDatasetPreviewRequestDto dataset)
        {
            GetDatasetPreviewResponseDto response = new GetDatasetPreviewResponseDto();
            GetDatasetRequest getDatasetRequest = new GetDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
            try
            {
                getDatasetRequest.Username = username;
                getDatasetRequest.Identifier = dataset.DatasetIdentifier;
                var reply = _client.GetDataset(getDatasetRequest);
                string datasetLocation = Path.Combine(controllerDatasetPath, username, reply.DatasetInfos.Identifier, reply.DatasetInfos.FileName);
                switch (reply.DatasetInfos.Type)
                {
                    case ":tabular":
                        response.DatasetPreview = File.ReadAllText(datasetLocation.Replace(".csv", "_preview.csv"));

                        break;
                    case ":image":
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
                    case ":longitudinal":
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
        /// Helper function, get all column names of a structured data dataset
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto dataset)
        {
            GetTabularDatasetColumnResponseDto response = new GetTabularDatasetColumnResponseDto();
            GetTabularDatasetColumnRequest getColumnNamesRequest = new GetTabularDatasetColumnRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getColumnNamesRequest.Username = username;
                getColumnNamesRequest.DatasetIdentifier = dataset.DatasetIdentifier;
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
        /// <summary>
        /// Upload a new dataset, currently only CSV are supported
        /// </summary>
        /// <param name="file"></param>
        /// <returns></returns>
        public async Task<ApiResponse> Upload(FileUploadRequestDto file)
        {
            UploadDatasetFileRequest request = new UploadDatasetFileRequest();
            try
            {
                var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
                string trustedFileNameForDisplay = WebUtility.HtmlEncode(file.FileName);
                string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
                var path = Path.Combine(controllerDatasetPath, username, "uploads");


                if (!Directory.Exists(path))
                {
                    Directory.CreateDirectory(path);
                }

                await using FileStream fs = new(Path.Combine(path, trustedFileNameForDisplay), FileMode.Append);
                fs.Write(file.Content, 0, file.Content.Length);

                //We uploaded everything, send grpc request to controller to persist
                if (file.ChunkNumber == file.TotalChunkNumber)
                {
                    fs.Dispose();
                    request.Username = username;
                    request.FileName = trustedFileNameForDisplay;
                    request.DatasetName = file.DatasetName;
                    request.Type = file.DatasetType;
                    var reply = _client.UploadDatasetFile(request);
                    return new ApiResponse(Status200OK, null, reply.ReturnCode);
                }
                return new ApiResponse(Status200OK, null, 0);
            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }            
        }

        public async Task<ApiResponse> UploadData(IFormFile file)
        {
            try
            {
                if (file == null || file.Length == 0)
                    return new ApiResponse(Status404NotFound, "File not selected");
                var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
                string trustedFileNameForDisplay = WebUtility.HtmlEncode(file.FileName);
                string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
                var path = Path.Combine(controllerDatasetPath, username, "uploads");

                if (!Directory.Exists(path))
                {
                    Directory.CreateDirectory(path);
                }

                await using FileStream fs = new(Path.Combine(path, trustedFileNameForDisplay), FileMode.Create);
                await file.CopyToAsync(fs);

                return new ApiResponse(Status200OK, null, trustedFileNameForDisplay);
            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
