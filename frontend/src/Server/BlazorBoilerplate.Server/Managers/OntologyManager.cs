using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Storage;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls which are connected to requests for knowledge from the Ontologie
    /// </summary>
    public class OntologyManager : IOntologyManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public OntologyManager(ApplicationDbContext dbContext, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }

        public async Task<ApiResponse> GetCompatibleAutoMlSolutions(GetCompatibleAutoMlSolutionsRequestDto request)
        {
            // call grpc method
            GetCompatibleAutoMlSolutionsRequest requestGrpc = new GetCompatibleAutoMlSolutionsRequest();
            GetCompatibleAutoMlSolutionsResponseDto response = new GetCompatibleAutoMlSolutionsResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                requestGrpc.Username = username;
                requestGrpc.Configuration.Add(request.Configuration);
                var reply = _client.GetCompatibleAutoMlSolutions(requestGrpc);
                response.AutoMlSolutions = await _cacheManager.GetObjectInformationList(reply.AutoMlSolutions.ToList());
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> GetSupportedMlLibraries(GetSupportedMlLibrariesRequestDto task)
        {
            // call grpc method
            GetSupportedMlLibrariesRequest requestGrpc = new GetSupportedMlLibrariesRequest();
            GetSupportedMlLibrariesResponseDto response = new GetSupportedMlLibrariesResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                requestGrpc.Username = username;
                requestGrpc.Task = task.Task;
                var reply = _client.GetSupportedMlLibraries(requestGrpc);
                response.MlLibraries = await _cacheManager.GetObjectInformationList(reply.MlLibraries.ToList());
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetDatasetCompatibleTasks(GetDatasetCompatibleTasksRequestDto dataset)
        {
            // call grpc method
            GetDatasetCompatibleTasksRequest request = new GetDatasetCompatibleTasksRequest();
            GetDatasetCompatibleTasksResponseDto response = new GetDatasetCompatibleTasksResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                request.Username = username;
                request.DatasetName = dataset.DatasetIdentifier;
                var reply = _client.GetDatasetCompatibleTasks(request);
                response.Tasks = await _cacheManager.GetObjectInformationList(reply.Tasks.ToList());
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
