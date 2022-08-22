using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Training;
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
    public class TrainingManager : ITrainingManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public TrainingManager(ApplicationDbContext dbContext, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
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
        public async Task<ApiResponse> GetTraining(GetTrainingRequestDto training)
        {
            GetTrainingRequest request = new GetTrainingRequest();
            GetTrainingResponseDto response = new GetTrainingResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                request.Username = username;    
                request.Id = training.TrainingId;
                var reply = _client.GetTraining(request);
                foreach (var automl in reply.Automls)
                {
                    var status = new Shared.Dto.AutoML.AutoMLStatusDto
                    {
                        ID = automl.Identifier,
                        Messages = automl.Messages.ToList(),
                        Status = automl.Status,
                        Name = (await _cacheManager.GetObjectInformation(automl.Name)).Properties["skos:prefLabel"],
                        TestScore = (double)automl.TestScore,
                        ValidationScore = (double)automl.ValidationScore,
                        Predictiontime = (double)automl.Predictiontime,
                        Runtime = (int)automl.Runtime
                    };
                    if (!string.IsNullOrEmpty(automl.Model))
                    {
                        status.Model = (await _cacheManager.GetObjectInformation(automl.Model)).Properties["skos:prefLabel"];
                        status.Library = (await _cacheManager.GetObjectInformation(automl.Library)).Properties["skos:prefLabel"];
                    }
                    else
                    {
                        status.Model = "";
                        status.Library = "";
                    }
                    response.AutoMls.Add(status);
                }
                response.Status = reply.Status;
                response.DatasetId = reply.DatasetId;
                response.DatasetName = reply.DatasetName;
                response.Task = await _cacheManager.GetObjectInformation(reply.Task);
                response.ID = reply.Identifier;
                response.StartTime = reply.StartTime.ToDateTime();

                response.Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.Configuration);
                response.DatasetConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.DatasetConfiguration);
                response.RuntimeConstraints = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(reply.RuntimeConstraints);

                //response.Configuration.Features = new Dictionary<string, BlazorBoilerplate.Server.DataType>();


                foreach (var mllibrarie in reply.RequiredMlLibraries)
                {
                    response.RequiredMlLibraries.Add(await _cacheManager.GetObjectInformation(mllibrarie));
                }

                foreach(var automl in reply.RequiredAutoMls)
                {
                    response.RequiredAutoMLs.Add(await _cacheManager.GetObjectInformation(automl));
                }


                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// retrieve all training ids
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetTrainingIds(GetTrainingIdsRequestDto training)
        {
            GetTrainingsRequest request = new GetTrainingsRequest();
            GetTrainingIdsResponseDto response = new GetTrainingIdsResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                request.Username = username;
                var reply = _client.GetTrainings(request);
                response.TrainingIds = reply.TrainingIds.ToList();
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// retrieve all trainings
        /// </summary>
        /// <param name="dataset"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetAllTrainings(GetAllTrainingsRequestDto training)
        {
            GetAllTrainingsRequest request = new GetAllTrainingsRequest();
            GetAllTrainingsResponseDto response = new GetAllTrainingsResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                request.Username = username;
                var reply = _client.GetAllTrainings(request);
                foreach (var train in reply.Trainings)
                {
                    GetTrainingResponseDto item = new GetTrainingResponseDto();
                    foreach (var automl in train.Automls)
                    {
                        item.AutoMls.Add(new Shared.Dto.AutoML.AutoMLStatusDto
                        {
                            ID = automl.Identifier,
                            Messages = automl.Messages.ToList(),
                            Status = automl.Status,
                            Name = (await _cacheManager.GetObjectInformation(automl.Name)).Properties["skos:prefLabel"],
                            Library = automl.Library,
                            Model = automl.Model,
                            TestScore = (double)automl.TestScore,
                            ValidationScore = (double)automl.ValidationScore,
                            Predictiontime = (double)automl.Predictiontime,
                            Runtime = (int)automl.Runtime
                        }); ;
                    }
                    item.ID = train.Identifier;
                    item.StartTime = train.StartTime.ToDateTime();
                    item.Status = train.Status;
                    item.DatasetId = train.DatasetId;
                    item.DatasetName = train.DatasetName;
                    item.Task = await _cacheManager.GetObjectInformation(train.Task);

                    item.Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(train.Configuration);
                    item.DatasetConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(train.DatasetConfiguration);
                    item.RuntimeConstraints = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(train.RuntimeConstraints);

                    //response.Configuration.Features = new Dictionary<string, BlazorBoilerplate.Server.DataType>();


                    foreach (var mllibrarie in train.RequiredMlLibraries)
                    {
                        item.RequiredMlLibraries.Add(await _cacheManager.GetObjectInformation(mllibrarie));
                    }

                    foreach (var automl in train.RequiredAutoMls)
                    {
                        item.RequiredAutoMLs.Add(await _cacheManager.GetObjectInformation(automl));
                    }
                    response.Trainings.Add(item);
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
