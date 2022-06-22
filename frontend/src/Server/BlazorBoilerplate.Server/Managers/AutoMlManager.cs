using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Storage;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using static Microsoft.AspNetCore.Http.StatusCodes;
using Google.Protobuf;
using Microsoft.AspNetCore.Http;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls related to AutoMl process
    /// </summary>
    public class AutoMlManager : IAutoMlManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        public AutoMlManager(ApplicationDbContext dbContext, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor)
        {
            _dbContext = dbContext;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
        }
        /// <summary>
        /// Get the result model from a specific AutoML
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetModel(GetAutoMlModelRequestDto autoMl)
        {
            GetAutoMlModelResponseDto response = new GetAutoMlModelResponseDto();
            GetAutoMlModelRequest getmodelRequest = new GetAutoMlModelRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getmodelRequest.Username = username;
                getmodelRequest.SessionId = autoMl.SessionId;
                getmodelRequest.AutoMl = autoMl.AutoMl;
                var reply = _client.GetAutoMlModel(getmodelRequest);
                response.Name = reply.Name;
                response.Content = reply.File.ToByteArray();
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Start the OMAML process to search for a model
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        public async Task<ApiResponse> Start(StartAutoMLRequestDto autoMl)
        {
            StartAutoMLResponseDto response = new StartAutoMLResponseDto();
            StartAutoMlProcessRequest startAutoMLrequest = new StartAutoMlProcessRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                startAutoMLrequest.Username = username;
                startAutoMLrequest.Dataset = autoMl.DatasetIdentifier;
        
                foreach (var i in autoMl.RequiredAutoMLs)
                {
                    startAutoMLrequest.RequiredAutoMls.Add(i);
                }
                startAutoMLrequest.Task = GetMachineLearningTask(autoMl);
                startAutoMLrequest.TabularConfig = GetTabularDataConfiguration(autoMl);
                // TODO consider to refactor
                startAutoMLrequest.RuntimeConstraints = new AutoMlRuntimeConstraints
                {
                    MaxIter = autoMl.RuntimeConstraints.Max_iter,
                    RuntimeLimit = autoMl.RuntimeConstraints.Runtime_limit
                };
                var reply = _client.StartAutoMlProcess(startAutoMLrequest);
                if (reply.Result == ControllerReturnCode.Success)
                {
                    response.SessionId = reply.SessionId;
                    return new ApiResponse(Status200OK, null, response);
                }
                else
                {
                    return new ApiResponse(Status400BadRequest, "Error while starting AutoML Code: " + reply.Result + "", null);
                }

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        public async Task<ApiResponse> TestAutoML(TestAutoMLRequestDto testAutoML)
        {
            TestAutoMLResponseDto response = new TestAutoMLResponseDto();
            TestAutoMlRequest testAutoMLrequest = new TestAutoMlRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                testAutoMLrequest.Username = username;
                testAutoMLrequest.TestData = testAutoML.TestData;
                testAutoMLrequest.SessionId = testAutoML.SessionId;
                testAutoMLrequest.AutoMlName = testAutoML.AutoMlName;

                var reply = _client.TestAutoML(testAutoMLrequest);

                response.Predictions.AddRange(reply.Predictions.ToList());
                response.Score = reply.Score;
                response.Predictiontime = reply.Predictiontime;
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Convert AutoML task to enum equivalent
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        private MachineLearningTask GetMachineLearningTask(StartAutoMLRequestDto autoMl)
        {
            switch (autoMl.DatasetType)
            {
                case "TABULAR":
                    switch (autoMl.Task)
                    {
                        case "tabular classification":
                            return MachineLearningTask.TabularClassification;
                        case "tabular regression":
                            return MachineLearningTask.TabularRegression;
                        default:
                            return MachineLearningTask.Unknown;
                    }
                default:
                    return MachineLearningTask.Unknown;
            }
        }
        /// <summary>
        /// retrive the Tabular data configuration accordingly to correct template
        /// Needed since a correct conversion requires explicit knowledge of the JSON structure
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        private AutoMlConfigurationTabularData GetTabularDataConfiguration(StartAutoMLRequestDto autoMl)
        {
            switch (autoMl.DatasetType)
            {
                case "TABULAR":
                    AutoMlConfigurationTabularData conf = new AutoMlConfigurationTabularData();
                    conf.Target = new AutoMlTarget();
                    conf.Target.Target = ((AutoMLTabularDataConfiguration)autoMl.Configuration).Target.Target;
                    conf.Target.Type = ((AutoMLTabularDataConfiguration)autoMl.Configuration).Target.Type;
                    // remove target from features
                    ((AutoMLTabularDataConfiguration)autoMl.Configuration).Features.Remove(((AutoMLTabularDataConfiguration)autoMl.Configuration).Target.Target);
                    conf.Features.Add(((AutoMLTabularDataConfiguration)autoMl.Configuration).Features);
                    return conf;
                default:
                    return null;
            }
        }
    }
}
