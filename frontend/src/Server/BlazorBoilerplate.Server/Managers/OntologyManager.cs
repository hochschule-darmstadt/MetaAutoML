using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Storage;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls which are connected to requests for knowledge from the Ontology
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

        public async Task<ApiResponse> GetAutoMlSolutionsForConfiguration(GetAutoMlSolutionsForConfigurationRequestDto request)
        {
            // call grpc method
            GetAutoMlSolutionsForConfigurationRequest requestGrpc = new GetAutoMlSolutionsForConfigurationRequest();
            GetAutoMlSolutionsForConfigurationResponseDto response;
            try
            {
                requestGrpc.Configuration.Add(request.Configuration);
                var reply = _client.GetAutoMlSolutionsForConfiguration(requestGrpc);
                response = new GetAutoMlSolutionsForConfigurationResponseDto(await _cacheManager.GetObjectInformationList(reply.AutoMlSolutions.ToList()));
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        public async Task<ApiResponse> GetTasksForDatasetType(GetTasksForDatasetTypeRequestDto request)
        {
            GetTasksForDatasetTypeRequest getTasksForDatasetTypeRequest = new GetTasksForDatasetTypeRequest();
            GetTasksForDatasetTypeResponseDto response;
            try
            {
                getTasksForDatasetTypeRequest.DatasetType = request.DatasetType;
                var reply = _client.GetTasksForDatasetType(getTasksForDatasetTypeRequest);
                response = new GetTasksForDatasetTypeResponseDto(await _cacheManager.GetObjectInformationList(reply.Tasks.ToList()));
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }


        /// <summary>
        /// Retrieve all Dataset Types
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

        public async Task<ApiResponse> GetMlLibrariesForTask(GetMlLibrariesForTaskRequestDto request)
        {
            // call grpc method
            GetMlLibrariesForTaskRequest requestGrpc = new GetMlLibrariesForTaskRequest();
            GetMlLibrariesForTaskResponseDto response;
            try
            {
                requestGrpc.Task = request.Task;
                var reply = _client.GetMlLibrariesForTask(requestGrpc);
                response = new GetMlLibrariesForTaskResponseDto(await _cacheManager.GetObjectInformationList(reply.MlLibraries.ToList()));
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> GetSearchRelevantData()
        {
            GetSearchRelevantDataResponseDto response;
            try
            {
                var reply = _client.GetSearchRelevantData(new GetSearchRelevantDataRequest());
                //TODO: use ontology keys to translate them and not whole object
                //response = new GetSearchRelevantDataResponseDto(await _cacheManager.GetObjectInformationList(reply.SearchEntities.ToList()));
                response = new GetSearchRelevantDataResponseDto(reply.SearchEntities.ToList());
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> GetAvailableStrategies(GetAvailableStrategiesRequestDto request)
        {
            // call grpc method
            GetAvailableStrategiesRequest requestGrpc = new GetAvailableStrategiesRequest();
            GetAvailableStrategiesResponseDto response = new GetAvailableStrategiesResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                requestGrpc.UserId = username;
                requestGrpc.DatasetId = request.DatasetId;
                requestGrpc.Configuration.Add(request.Configuration);
                var reply = _client.GetAvailableStrategies(requestGrpc);
                response.Strategies = new List<StrategyControllerStrategyDto>();
                foreach(var strategy in reply.Strategies.ToList()) {
                    StrategyControllerStrategyDto strategyDto = new StrategyControllerStrategyDto(strategy);
                    response.Strategies.Add(strategyDto);
                }
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> GetAutoMlParameters(GetAutoMlParametersRequestDto request)
        {
            var requestParams = new GetAutoMlParametersRequest { TaskIri = request.TaskIri };
            requestParams.AutoMls.AddRange(request.AutoMls);
            var response = new GetAutoMlParametersResponseDto();
            try
            {
                var grpcResponse = await _client.GetAutoMlParametersAsync(requestParams);
                var results = await Task.WhenAll(grpcResponse.AutoMlParameters.Select(async p => new AutoMlParameterDto(
                    await _cacheManager.GetObjectInformation(p.AutoMlIri),
                    await _cacheManager.GetObjectInformation(p.ParamIri),
                    await _cacheManager.GetObjectInformation(p.ParamType),
                    await _cacheManager.GetObjectInformation(p.BroaderIri),
                    await _cacheManager.GetObjectInformation(p.ValueIri))));
                response.AutoMlParameters = results.ToList();
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
