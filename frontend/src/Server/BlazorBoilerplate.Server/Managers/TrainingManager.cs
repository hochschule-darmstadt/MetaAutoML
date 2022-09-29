using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Training;
using Newtonsoft.Json;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls related to the AutoML sessions
    /// </summary>
    public class TrainingManager : ITrainingManager
    {
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public TrainingManager(ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }
        /// <summary>
        /// Start the OMAML process to search for a model
        /// </summary>
        /// <param name="autoMl"></param>
        /// <returns></returns>
        public async Task<ApiResponse> CreateTraining(CreateTrainingRequestDto request)
        {
            CreateTrainingRequest createTrainingRequest = new CreateTrainingRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                createTrainingRequest.UserIdentifier = username;
                createTrainingRequest.DatasetIdentifier = request.DatasetIdentifier;
                createTrainingRequest.Task = request.Task;
                createTrainingRequest.Configuration = JsonConvert.SerializeObject(request.Configuration);

                foreach (var i in request.SelectedAutoMLs)
                {
                    createTrainingRequest.SelectedAutoMls.Add(i);
                }
                createTrainingRequest.RuntimeConstraints = JsonConvert.SerializeObject(request.RuntimeConstraints);
                createTrainingRequest.DatasetConfiguration = JsonConvert.SerializeObject(request.DatasetConfiguration);
                createTrainingRequest.TestConfiguration = JsonConvert.SerializeObject(request.TestConfiguration);
                createTrainingRequest.Metric = request.Metric;
                foreach (var i in request.SelectedMlLibraries)
                {
                    createTrainingRequest.SelectedLibraries.Add(i);
                }
                var reply = _client.CreateTraining(createTrainingRequest);
                return new ApiResponse(Status200OK, null, new CreateTrainingResponseDto(reply.TrainingIdentifier));

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
        public async Task<ApiResponse> GetTrainings()
        {
            GetTrainingsRequest getTrainings = new GetTrainingsRequest();
            GetTrainingsResponseDto response = new GetTrainingsResponseDto();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getTrainings.UserIdentifier = username;
                var reply = _client.GetTrainings(getTrainings);
                foreach (var training in reply.Trainings)
                {
                    TrainingDto trainingDto = new TrainingDto(training, await _cacheManager.GetObjectInformation(training.Task));
                    foreach (var model in training.Models)
                    {
                        ModelDto modelDto = new ModelDto(model, 
                            (model.MlModelType == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() :  await _cacheManager.GetObjectInformation(model.MlModelType)),
                            (model.MlLibrary == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() : await _cacheManager.GetObjectInformation(model.MlLibrary)),
                            (model.Automl == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() : await _cacheManager.GetObjectInformation(model.Automl)));
                        trainingDto.models.Add(modelDto);
                    }
                    trainingDto.SelectedMlLibraries = await _cacheManager.GetObjectInformationList(training.SelectedMlLibraries.ToList());
                    trainingDto.SelectedAutoMls = await _cacheManager.GetObjectInformationList(training.SelectedAutoMls.ToList());
                    response.Trainings.Add(trainingDto);
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Get informations about a specific session
        /// </summary>
        /// <param name="session"></param>
        /// <returns></returns>
        public async Task<ApiResponse> GetTraining(GetTrainingRequestDto request)
        {
            GetTrainingRequest getTrainingRequest = new GetTrainingRequest();
            GetTrainingResponseDto response;
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                getTrainingRequest.UserIdentifier = username;
                getTrainingRequest.TrainingIdentifier = request.TrainingIdentifier;
                GetTrainingResponse reply = _client.GetTraining(getTrainingRequest);
                response = new GetTrainingResponseDto(new TrainingDto(reply.Training, await _cacheManager.GetObjectInformation(reply.Training.Task)));
                foreach (var model in reply.Training.Models)
                {
                    ModelDto modelDto = new ModelDto(model,
                            (model.MlModelType == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() : await _cacheManager.GetObjectInformation(model.MlModelType)),
                            (model.MlLibrary == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() : await _cacheManager.GetObjectInformation(model.MlLibrary)),
                            (model.Automl == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() : await _cacheManager.GetObjectInformation(model.Automl)));
                    response.Training.models.Add(modelDto);
                }
                response.Training.SelectedMlLibraries = await _cacheManager.GetObjectInformationList(reply.Training.SelectedMlLibraries.ToList());
                response.Training.SelectedAutoMls = await _cacheManager.GetObjectInformationList(reply.Training.SelectedAutoMls.ToList());


                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
        /// <summary>
        /// Delete a training
        /// </summary>
        /// <returns></returns>
        public async Task<ApiResponse> DeleteTraining(DeleteTrainingRequestDto request)
        {
            DeleteTrainingRequest deleteTrainingsRequest = new DeleteTrainingRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                deleteTrainingsRequest.TrainingIdentifier = request.TrainingIdentifier;
                deleteTrainingsRequest.UserIdentifier = username;
                var reply = _client.DeleteTraining(deleteTrainingsRequest);
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
