using BlazorBoilerplate.Constants;
using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Storage;
using Grpc.Core;
using Grpc.Net.Client;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
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
                response = new GetDatasetResponseDto(
                    reply.DatasetInfos.Name,
                    await _cacheManager.GetObjectInformation(reply.DatasetInfos.Type),
                    reply.DatasetInfos.Columns,
                    reply.DatasetInfos.Rows,
                    reply.DatasetInfos.CreationDate.ToDateTime(),
                    reply.DatasetInfos.Identifier);

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
                    response.Datasets.Add(new GetDatasetResponseDto(item.Name, typeInformation, item.Columns, item.Rows,item.CreationDate.ToDateTime(), item.Identifier));
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
                        FirstEntries = item.FirstEntries.ToList()
                    });
                }
                response.ConvertColumnsToRows();
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
                request.Username = username;
                request.FileName = file.FileName;
                request.DatasetName = file.DatasetName;
                request.Type = file.DatasetType;
                request.Content = Google.Protobuf.ByteString.CopyFrom(file.Content);
                var reply = _client.UploadDatasetFile(request);
                return new ApiResponse(Status200OK, null, reply.ReturnCode);
            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }            
        }
    }
}
