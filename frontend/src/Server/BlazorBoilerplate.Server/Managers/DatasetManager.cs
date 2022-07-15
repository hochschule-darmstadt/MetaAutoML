﻿using BlazorBoilerplate.Constants;
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
            List<GetDatasetResponseDto> response = new List<GetDatasetResponseDto>();
            GetDatasetRequest getDatasetRequest = new GetDatasetRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getDatasetRequest.Username = username;
                getDatasetRequest.Identifier = dataset.Name;
                var reply = _client.GetDataset(getDatasetRequest);
                foreach (var item in reply.Columns)
                {
                    response.Add(new GetDatasetResponseDto
                    {
                        Name = item.Name,
                        Type = (Server.DataType)item.Type,
                        ConvertibleTypes = item.ConvertibleTypes.ToList(),
                        FirstEntries = item.FirstEntries.ToList()
                    }) ;
                }
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
            List<GetDatasetsResponseDto> response = new List<GetDatasetsResponseDto>();
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
                    response.Add(new GetDatasetsResponseDto(item.FileName, typeInformation, item.Columns, item.Rows,item.CreationDate.ToDateTime(), item.Identifier));
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
        public async Task<ApiResponse> GetTabularDatasetColumnNames(GetTabularDatasetColumnNamesRequestDto dataset)
        {
            GetTabularDatasetColumnNamesResponseDto response = new GetTabularDatasetColumnNamesResponseDto();
            GetTabularDatasetColumnNamesRequest getColumnNamesRequest = new GetTabularDatasetColumnNamesRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getColumnNamesRequest.Username = username;
                getColumnNamesRequest.DatasetName = dataset.DatasetName;
                var reply = _client.GetTabularDatasetColumnNames(getColumnNamesRequest);
                response.ColumnNames.AddRange(reply.ColumnNames.ToList());
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
