using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Storage;
using Newtonsoft.Json;
using System.Net;
using UtfUnknown;
using static Microsoft.AspNetCore.Http.StatusCodes;
using System.IO.Compression;
using Microsoft.AspNetCore.SignalR;
using System.Net.Http;
using System.Security.Policy;
using BlazorBoilerplate.Server.Hubs;
using Microsoft.AspNetCore.Mvc;
using System.Text;
using System;
using NuGet.Protocol.Plugins;
using System.Text.Json;
using System.Text.RegularExpressions;

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
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly IHubContext<UploadHub> _uploadHubContext;
        public DatasetManager(ApplicationDbContext dbContext, ILogger<EmailManager> logger, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager, IHubContext<UploadHub> uploadHubContext, IHttpClientFactory httpClientFactory)
        {
            _dbContext = dbContext;
            _logger = logger;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
            _httpClientFactory = httpClientFactory;
            _uploadHubContext = uploadHubContext;
        }
        /// <summary>
        /// Upload a new dataset; currently CSV, XLSX, XLS and ARFF are supported
        /// </summary>
        /// <param name="request"></param>
        /// <returns></returns>
        //public async Task<ApiResponse> UploadDataset(UploadDatasetRequestDto request)
        //{
        //    CreateDatasetRequest grpcRequest = new CreateDatasetRequest();
        //    try
        //    {
        //        var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
        //        string trustedFileNameForDisplay = WebUtility.HtmlEncode(request.FileNameOrURL);
        //        string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
        //        var path = Path.Combine(controllerDatasetPath, username, "uploads");

        //        if (request.ChunkNumber == 1)
        //        {
        //            var dir = new DirectoryInfo(path);

        //            foreach (var info in dir.GetFiles())
        //            {
        //                info.Delete();
        //            }
        //        }

        //        if (!Directory.Exists(path))
        //        {
        //            Directory.CreateDirectory(path);
        //        }

        //        await using FileStream fs = new(Path.Combine(path, trustedFileNameForDisplay), FileMode.Append);
        //        fs.Write(request.Content, 0, request.Content.Length);

        //        // get the complete file path before fs is released
        //        string filePath = path + "/" + Path.GetFileName(fs.Name);

        //        if (request.ChunkNumber == request.TotalChunkNumber)
        //        {
        //            fs.Dispose();

        //            string fileExt = Path.GetExtension(filePath);
        //            if (!CheckSupportedFileType(fileExt))
        //            {
        //                return new ApiResponse(Status406NotAcceptable, "FileTypeNotSupportedErrorMessage");
        //            }
        //            if (fileExt == ".zip" && !CheckZIPStructure(filePath))
        //            {
        //                return new ApiResponse(Status406NotAcceptable, "FolderStructureNotCorrectErrorMessage");
        //            }

        //            grpcRequest.DatasetType = request.DatasetType;
        //            DetectionResult result;
        //            if (grpcRequest.DatasetType == ":text" || grpcRequest.DatasetType == ":tabular" || grpcRequest.DatasetType == ":time_series" || grpcRequest.DatasetType == ":time_series_longitudinal")
        //            {
        //                using (FileStream fs1 = new FileStream(Path.Combine(path, trustedFileNameForDisplay), FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
        //                {
        //                    result = CharsetDetector.DetectFromStream(fs1);

        //                }
        //                if (result.Detected == null)
        //                {
        //                    // Ignore the encoding of XLSX and XLS files
        //                    if (fileExt != ".xlsx" && fileExt != ".xls")
        //                    {
        //                        return new ApiResponse(Status406NotAcceptable, "EncodingNotSupportedErrorMessage");
        //                    }
        //                    grpcRequest.Encoding = "utf-8";
        //                }
        //                else
        //                {
        //                    grpcRequest.Encoding = result.Detected.EncodingName.ToString();
        //                    //ascii data encoding causes some issues with some automl, UTF-8 is a safe encoding that covers all ascii signs
        //                    if (grpcRequest.Encoding == "ascii")
        //                    {
        //                        grpcRequest.Encoding = "utf-8";
        //                    }
        //                }
        //            }
        //            else
        //            {
        //                grpcRequest.Encoding = "";
        //            }

        //            grpcRequest.UserId = username;
        //            grpcRequest.FileName = trustedFileNameForDisplay;
        //            grpcRequest.DatasetName = request.DatasetName;
        //            grpcRequest.DatasetType = request.DatasetType;
        //            var reply = _client.CreateDataset(grpcRequest);
        //            return new ApiResponse(Status200OK, null, "");
        //        }
        //        return new ApiResponse(Status200OK, null, "");
        //    }
        //    catch (Exception ex)
        //    {
        //        return new ApiResponse(Status404NotFound, ex.Message);
        //    }
        //}

        private string GetDatasetEncoding(string datasetType, string filePath, string fileExt)
        {
            DetectionResult result;

            if (datasetType == ":text" || datasetType == ":tabular" || datasetType == ":time_series" || datasetType == ":time_series_longitudinal")
            {
                using (FileStream fs1 = new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                {
                    result = CharsetDetector.DetectFromStream(fs1);

                }
                if (result.Detected == null)
                {
                    // Ignore the encoding of XLSX and XLS files
                    if (fileExt != ".xlsx" && fileExt != ".xls")
                    {
                        return null;
                    }
                    return "utf-8";
                }
                else
                {
                    var encoding = result.Detected.EncodingName.ToString();
                    //ascii data encoding causes some issues with some automl, UTF-8 is a safe encoding that covers all ascii signs
                    if (encoding == "ascii")
                    {
                        return "utf-8";
                    }
                }
            }
            else
            {
                return null;
            }
            return null;
        }

        public async Task<ApiResponse> UploadFromDisk(UploadDatasetRequestDto request)
        {
            try
            {
                CreateDatasetRequest grpcRequest = new CreateDatasetRequest();
                var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
                string trustedFileNameForDisplay = WebUtility.HtmlEncode(request.File.FileName);
                string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
                var path = Path.Combine(controllerDatasetPath, username, "uploads");

                var filePath = Path.Combine("uploads", username, WebUtility.HtmlEncode(request.File.FileName) + Path.GetExtension(request.File.FileName));
                Directory.CreateDirectory(Path.GetDirectoryName(filePath));

                await using var fileStream = new FileStream(Path.Combine(path, trustedFileNameForDisplay), FileMode.Create, FileAccess.Write, FileShare.None, 8192, true);

                var totalBytes = request.File.Length;
                var buffer = new byte[81920]; // 80KB buffer
                long totalBytesRead = 0;
                double progress = 0;
                using (var inputStream = request.File.OpenReadStream())
                {
                    int bytesRead;
                    while ((bytesRead = await inputStream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                    {
                        await fileStream.WriteAsync(buffer, 0, bytesRead);
                        totalBytesRead += bytesRead;

                        // Calculate progress
                        var newProgress = (int)((double)totalBytesRead / totalBytes * 100);
                        if (newProgress != progress)
                        {
                            progress = newProgress;
                            await _uploadHubContext.Clients.Client(request.SignalrConnectionId).SendAsync("UploadDatasetProgress", progress);
                        }
                    }
                }
                fileStream.Close();
                await _uploadHubContext.Clients.Client(request.SignalrConnectionId).SendAsync("UploadDatasetComplete", "ok");


                grpcRequest.DatasetType = request.DatasetType;
                string fileExt = Path.GetExtension(filePath);
                if (!CheckSupportedFileType(fileExt))
                {
                    return new ApiResponse(Status406NotAcceptable, "FileTypeNotSupportedErrorMessage");
                }
                if (fileExt == ".zip" && !CheckZIPStructure(filePath))
                {
                    return new ApiResponse(Status406NotAcceptable, "FolderStructureNotCorrectErrorMessage");
                }
                grpcRequest.Encoding = GetDatasetEncoding(request.DatasetType, Path.Combine(path, trustedFileNameForDisplay), fileExt);
                grpcRequest.UserId = username;
                grpcRequest.FileName = trustedFileNameForDisplay;
                grpcRequest.DatasetName = request.DatasetName;
                grpcRequest.DatasetType = request.DatasetType;
                var reply = _client.CreateDataset(grpcRequest);


                return new ApiResponse(Status200OK, null, "");
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }

        }

        public async Task<ApiResponse> UploadFromUrl(UploadDatasetRequestDto request)
        {
            try
            {
                CreateDatasetRequest grpcRequest = new CreateDatasetRequest();
                var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
                string trustedFileNameForDisplay = WebUtility.HtmlEncode(request.DatasetName);
                string controllerDatasetPath = Environment.GetEnvironmentVariable("CONTROLLER_DATASET_FOLDER_PATH");
                var path = Path.Combine(controllerDatasetPath, username, "uploads");

                string fileType = "";
                string downloadUrl = GetDownloadUrl(request.Url);
                var httpClient = _httpClientFactory.CreateClient();
                var response = await httpClient.GetAsync(downloadUrl, HttpCompletionOption.ResponseHeadersRead);

                response.EnsureSuccessStatusCode();

                string _fileExtension =
                        (response.Content.Headers.ContentDisposition?.FileNameStar ??
                        response.Content.Headers.ContentDisposition?.FileName)?
                        .Split('.').LastOrDefault()?.TrimEnd('"') ?? string.Empty;
                switch (request.DatasetType)
                {
                    case ":tabular":
                        fileType = ".csv, .arff, .xlsx, .xls";
                        break;
                    case ":image":
                        fileType = ".zip";
                        break;
                    case ":text":
                        fileType = ".csv, .arff, .xlsx, .xls";
                        break;
                    case ":time_series":
                        fileType = ".csv, .arff, .xlsx, .xls";
                        break;
                    case ":time_series_longitudinal":
                        fileType = ".ts";
                        break;
                }
                fileType = !string.IsNullOrEmpty(_fileExtension) ? $".{_fileExtension}" : fileType.Split(',')[0];

                var totalBytes = response.Content.Headers.ContentLength ?? -1L;
                var canReportProgress = totalBytes != -1;

                var filePath = Path.Combine("uploads", username, WebUtility.HtmlEncode(request.DatasetName) + fileType);
                Directory.CreateDirectory(Path.GetDirectoryName(filePath));

                await using var contentStream = await response.Content.ReadAsStreamAsync();
                await using var fileStream = new FileStream(Path.Combine(path, trustedFileNameForDisplay + fileType), FileMode.Create, FileAccess.Write, FileShare.None, 8192, true);

                var buffer = new byte[8192];
                long totalReadBytes = 0;
                int readBytes;

                while ((readBytes = await contentStream.ReadAsync(buffer)) > 0)
                {
                    await fileStream.WriteAsync(buffer.AsMemory(0, readBytes));
                    totalReadBytes += readBytes;

                    if (canReportProgress)
                    {
                        var progress = (double)totalReadBytes / totalBytes * 100;
                        await _uploadHubContext.Clients.Client(request.SignalrConnectionId).SendAsync("UploadDatasetProgress", progress);
                    }
                }
                fileStream.Close();

                await _uploadHubContext.Clients.Client(request.SignalrConnectionId).SendAsync("UploadDatasetComplete", "ok");
                grpcRequest.DatasetType = request.DatasetType;
                string fileExt = Path.GetExtension(filePath);
                if (!CheckSupportedFileType(fileExt))
                {
                    return new ApiResponse(Status406NotAcceptable, "FileTypeNotSupportedErrorMessage");
                }
                if (fileExt == ".zip" && !CheckZIPStructure(filePath))
                {
                    return new ApiResponse(Status406NotAcceptable, "FolderStructureNotCorrectErrorMessage");
                }
                grpcRequest.Encoding = GetDatasetEncoding(request.DatasetType, Path.Combine(path, trustedFileNameForDisplay + fileType), fileExt);
                grpcRequest.UserId = username;
                grpcRequest.FileName = trustedFileNameForDisplay + fileType;
                grpcRequest.DatasetName = request.DatasetName;
                grpcRequest.DatasetType = request.DatasetType;
                var reply = _client.CreateDataset(grpcRequest);

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
        public async Task<ApiResponse> GetDatasets(GetDatasetsRequestDto request)
        {
            GetDatasetsResponseDto response = new GetDatasetsResponseDto();
            GetDatasetsRequest getDatasetsRequest = new GetDatasetsRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetsRequest.Type = "";
                getDatasetsRequest.UserId = username;
                getDatasetsRequest.OnlyFiveRecent = request.OnlyFiveRecent;
                getDatasetsRequest.Pagination = request.Pagination;
                getDatasetsRequest.PageNumber = request.PageNumber;
                var reply = _client.GetDatasets(getDatasetsRequest);
                foreach (Dataset item in reply.Datasets)
                {
                    Dictionary<string, Shared.Dto.Dataset.ColumnSchemaDto> schema = new Dictionary<string, Shared.Dto.Dataset.ColumnSchemaDto>();
                    //foreach (var column in item.Schema)
                    //{
                    //    schema.Add(column.Key, new Shared.Dto.Dataset.ColumnSchemaDto(
                    //        await _cacheManager.GetObjectInformation(column.Value.DatatypeDetected),
                    //        await _cacheManager.GetObjectInformationList(column.Value.DatatypesCompatible.ToList()),
                    //        column.Value.DatatypeSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.DatatypeSelected),
                    //        await _cacheManager.GetObjectInformationList(column.Value.RolesCompatible.ToList()),
                    //        column.Value.RoleSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.RoleSelected)));
                    //}
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
                        column.Value.RoleSelected == "" ? new ObjectInfomationDto() : await _cacheManager.GetObjectInformation(column.Value.RoleSelected),
                        column.Value.Preprocessing));
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
                // check if analysis for yprofilling exist, set to the bool in dto
                if (analysis != null)
                {
                    if (analysis.ContainsKey("report_html_path")) response.ydataprofilling = analysis["report_html_path"];
                    else response.ydataprofilling = null;
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
        /// Check if the file extension is supported
        /// </summary>
        /// <param name="fileExt"></param>
        /// <returns></returns>
        private bool CheckSupportedFileType(string fileExt)
        {
            if (fileExt == ".csv" || fileExt == ".arff" || fileExt == ".xlsx" || fileExt == ".xls" || fileExt == ".zip")
            {
                return true;
            }
            return false;
        }

        /// <summary>
        /// Check if the ZIP archive has the correct structure
        /// </summary>
        /// <param name="filePath"></param>
        /// <returns></returns>
        private bool CheckZIPStructure(string filePath)
        {
            List<string> zipEntries = new List<string>();
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


        /// <summary>
        /// Get the download URL for a given URL of supported cloud storage services
        /// </summary>
        /// <param name="url">The URL entered by the user.</param>
        /// <returns>direct download link</returns>
        private static string GetDownloadUrl(string url)
        {
            if (Regex.IsMatch(url, @"(?:drive\.google\.com|docs\.google\.com)"))
            {
                return GetGoogleDriveDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:\.dropbox\.com)"))
            {
                return GetDropboxDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:1drv\.ms|i\.s!)"))
            {
                return GetOnedriveDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:sharepoint\.com)"))
            {
                return GetSharepointDownloadLink(url);
            }
            else if (Regex.IsMatch(url, @"(?:cloud\.h-da\.de)"))
            {
                return GetNextcloudDownloadLink(url);
            }
            if (Regex.IsMatch(url, @"(?:openml\.org/search).*type=data"))
            {
                return GetOpenMLDownloadLink(url);
            }
            return url;
        }
        /// <summary>
        /// Get the direct download URL for Google Drive using the file id
        /// </summary>
        /// <param name="googleDriveUrl">Google Drive URL</param>
        /// <returns>Direct download URL for Google Drive</returns>
        private static string GetGoogleDriveDownloadLink(string googleDriveUrl)
        {
            var match = Regex.Match(googleDriveUrl, @"/d/([a-zA-Z0-9_-]+)");
            if (match.Success && match.Groups.Count > 1)
            {
                string fileId = match.Groups[1].Value;
                googleDriveUrl = $"https://drive.google.com/uc?id={fileId}&export=download&confirm=t";
                return googleDriveUrl;
            }
            return googleDriveUrl;
        }

        /// <summary>
        /// Get the direct download URL for Dropbox
        /// </summary>
        /// <param name="dropboxUrl">Dropbox URL</param>
        /// <returns>Direct Download URL for Dropbox</returns>
        private static string GetDropboxDownloadLink(string dropboxUrl)
        {
            if (dropboxUrl.EndsWith("&dl=0"))
            {
                return dropboxUrl.Replace("&dl=0", "&dl=1");
            }
            if (!dropboxUrl.EndsWith("&dl=1"))
            {
                return dropboxUrl + "&dl=1";
            }
            return dropboxUrl;
        }

        /// <summary>
        /// Get the direct download URL for OneDrive by encoding the Base64 decoded URL
        /// </summary>
        /// <param name="onedriveUrl">OneDrive URL</param>
        /// <returns>Direct download URL for Onedrive</returns>
        private static string GetOnedriveDownloadLink(string onedriveUrl)
        {
            string base64Value = System.Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(onedriveUrl));
            string encodedUrl = base64Value.TrimEnd('=').Replace('/', '_').Replace('+', '-');
            onedriveUrl = $"https://api.onedrive.com/v1.0/shares/u!{encodedUrl}/root/content";
            return onedriveUrl;
        }

        /// <summary>
        /// Get the direct download URL for Sharepoint
        /// </summary>
        /// <param name="sharepointUrl">Sharepoint URL</param>
        /// <returns>Direct download URL for Sharepoint</returns>
        private static string GetSharepointDownloadLink(string sharepointUrl)
        {
            if (sharepointUrl.Contains("&download=1"))
            {
                return sharepointUrl;
            }
            return sharepointUrl + "&download=1";
        }

        /// <summary>
        /// Get the direct download URL for h_da Nextcloud
        /// </summary>
        /// <param name="nextcloudUrl">h_da Nextcloud URL</param>
        /// <returns>Direct download URL for h_da Nextcloud</returns>
        private static string GetNextcloudDownloadLink(string nextcloudUrl)
        {
            if (nextcloudUrl.EndsWith("/download"))
            {
                return nextcloudUrl;
            }
            return nextcloudUrl + "/download";
        }

        /// <summary>
        /// Get the direct download URL for OpenML datasets by using the OpenML API
        /// </summary>
        /// <param name="openMLUrl">OpenML URL</param>
        /// <returns>Direct download URL for OpenML datasets</returns>
        private static string GetOpenMLDownloadLink(string openMLUrl)
        {
            var match = Regex.Match(openMLUrl, @"(?:\b|\?)id=(\d+)\b");
            if (match.Success)
            {
                string datasetId = match.Groups[1].Value;
                string apiUrl = $"https://www.openml.org/api/v1/json/data/{datasetId}";
                try
                {
                    using (var client = new HttpClient())
                    {
                        HttpResponseMessage response = client.GetAsync(apiUrl).Result;
                        if (response.IsSuccessStatusCode)
                        {
                            JsonDocument jsonDocument = JsonDocument.Parse(response.Content.ReadAsStringAsync().Result);
                            JsonElement urlElement = jsonDocument.RootElement.GetProperty("data_set_description").GetProperty("url");
                            openMLUrl = urlElement.GetString();
                            return openMLUrl;
                        }
                    }
                }
                catch (Exception ex)
                {
                }
            }
            return openMLUrl;
        }

    }
}
