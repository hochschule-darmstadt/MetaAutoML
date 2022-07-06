using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Session;
using BlazorBoilerplate.Storage;
using Google.Protobuf.Collections;
using Google.Protobuf.WellKnownTypes;
using Microsoft.AspNetCore.Http;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls related to the AutoML sessions
    /// </summary>
    public class SessionManager : ISessionManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public SessionManager(ApplicationDbContext dbContext, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;   
        }
        /// <summary>
        /// Get informations about a specific session
        /// </summary>
        /// <param name="session"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetSession(GetSessionRequestDto session)
        {
            GetSessionStatusRequest request = new GetSessionStatusRequest();
            GetSessionResponseDto response = new GetSessionResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                request.Username = username;    
                request.Id = session.SessionId;
                var reply = _client.GetSessionStatus(request);
                foreach (var automl in reply.Automls)
                {
                    response.AutoMls.Add(new Shared.Dto.AutoML.AutoMLStatusDto
                    {
                        Messages = automl.Messages.ToList(),
                        Status = automl.Status,
                        Name = (await _cacheManager.GetObjectInformation(automl.Name)).Properties["skos:prefLabel"],
                        Library = automl.Library,
                        Model = automl.Model,
                        TestScore = (double) automl.TestScore,
                        ValidationScore = (double) automl.ValidationScore,
                        Predictiontime = (double) automl.Predictiontime,
                        Runtime = (int)automl.Runtime
                    });
                }
                response.Status = reply.Status;
                response.DatasetId = reply.DatasetId;
                response.DatasetName = reply.DatasetName;
                response.Task = reply.Task;

                response.Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.Configuration);
                response.DatasetConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.DatasetConfiguration);
                response.RuntimeConstraints = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.RuntimeConstraints);

                //response.Configuration.Features = new Dictionary<string, BlazorBoilerplate.Server.DataType>();


                foreach (var mllibrarie in reply.RequiredMlLibraries)
                {
                    response.RequiredMlLibraries.Add(mllibrarie);
                }

                foreach(var automl in reply.RequiredAutoMls)
                {
                    response.RequiredAutoMLs.Add(automl);
                }


                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// retrieve all session ids
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetSessions(GetSessionsRequestDto dataset)
        {
            GetSessionsRequest request = new GetSessionsRequest();
            GetSessionsResponseDto response = new GetSessionsResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                request.Username = username;
                var reply = _client.GetSessions(request);
                response.SessionIds = reply.SessionIds.ToList();
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
