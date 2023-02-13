using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Training;
using BlazorBoilerplate.Theme.Material.Demo.Pages;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Org.BouncyCastle.Tls;
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

        private string ConvertDatasetSchemaToString(Dictionary<string, ColumnSchemaDto> schema)
        {
            Dictionary<string, ColumnSchema> columns = new Dictionary<string, ColumnSchema>();
            foreach (var column in schema)
            {
                ColumnSchema columnSchema = new ColumnSchema();
                columnSchema.DatatypeDetected = column.Value.DatatypeDetected.ID;
                columnSchema.DatatypesCompatible.AddRange(column.Value.DatatypesCompatible.Select(a => a.ID).ToArray());
                columnSchema.DatatypeSelected = column.Value.DatatypeSelected.ID == null ? "" : column.Value.DatatypeSelected.ID;
                columnSchema.RolesCompatible.AddRange(column.Value.RolesCompatible.Select(a => a.ID).ToArray());
                columnSchema.RoleSelected = column.Value.RoleSelected.ID == null ? "" : column.Value.RoleSelected.ID;
                columns[column.Key] = columnSchema;
            }
            return JsonConvert.SerializeObject(columns);
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
                createTrainingRequest.UserId = username;
                createTrainingRequest.DatasetId = request.DatasetId;
                createTrainingRequest.Configuration = new Configuration
                {
                    Task = request.Configuration.Task,
                    RuntimeLimit = request.Configuration.RuntimeLimit,
                    Metric = request.Configuration.Metric
                };
                createTrainingRequest.Configuration.SelectedAutoMlSolutions.AddRange(request.Configuration.SelectedAutoMlSolutions);
                createTrainingRequest.Configuration.SelectedMlLibraries.AddRange(request.Configuration.SelecctedMlLibraries);
                createTrainingRequest.Configuration.EnabledStrategies.AddRange(request.Configuration.EnabledStrategies);
                foreach (var param in request.Configuration.Parameters)
                {
                    var dynamicParameterValue = new DynamicParameterValue();
                    dynamicParameterValue.Values.AddRange(param.Values);
                    createTrainingRequest.Configuration.Parameters.Add(param.Iri, dynamicParameterValue);
                }
                createTrainingRequest.DatasetConfiguration = ConvertDatasetSchemaToString(request.Schema);
                createTrainingRequest.SaveSchema = request.SaveSchema;
                var reply = await _client.CreateTrainingAsync(createTrainingRequest);
                return new ApiResponse(Status200OK, null, new CreateTrainingResponseDto(reply.TrainingId));

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
                getTrainings.UserId = username;
                var reply = _client.GetTrainings(getTrainings);
                foreach (var training in reply.Trainings)
                {
                    TrainingDto trainingDto = await CreateTrainingDtoFromTraining(username, training);
                    response.Trainings.Add(trainingDto);
                }
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }

        private async Task<TrainingDto> CreateTrainingDtoFromTraining(string username, Training training)
        {
            GetDatasetResponse dataset = _client.GetDataset(new GetDatasetRequest { DatasetId = training.DatasetId, UserId = username });
            TrainingDto trainingDto = new TrainingDto(training, dataset.Dataset.Name);
            trainingDto.Configuration.Task = await _cacheManager.GetObjectInformation(training.Configuration.Task);
            trainingDto.Configuration.Target = training.Configuration.Target;
            trainingDto.Configuration.EnabledStrategies.AddRange(training.Configuration.EnabledStrategies);
            trainingDto.Configuration.RuntimeLimit = training.Configuration.RuntimeLimit;
            trainingDto.Configuration.Metric = await _cacheManager.GetObjectInformation(training.Configuration.Metric);
            foreach (var item in training.Configuration.SelectedAutoMlSolutions)
            {
                trainingDto.Configuration.SelectedAutoMlSolutions.Add(await _cacheManager.GetObjectInformation(item));
            }
            foreach (var item in training.Configuration.SelectedMlLibraries)
            {
                trainingDto.Configuration.SelecctedMlLibraries.Add(await _cacheManager.GetObjectInformation(item));
            }

            foreach (var model in training.Models)
            {
                List<Metric> metrics = new List<Metric>();
                foreach (var metric in JObject.Parse(model.TestScore))
                {
                    metrics.Add(new Metric() { Name = await _cacheManager.GetObjectInformation(metric.Key), Score = (float)metric.Value });

                }
                ModelDto modelDto = new ModelDto(model,
                    (model.MlModelType.Count() == 0 ? new List<Shared.Dto.Ontology.ObjectInfomationDto>() : await _cacheManager.GetObjectInformationList(model.MlModelType.ToList())),
                    (model.MlLibrary.Count() == 0 ? new List<Shared.Dto.Ontology.ObjectInfomationDto>() : await _cacheManager.GetObjectInformationList(model.MlLibrary.ToList())),
                    (model.AutoMlSolution == "" ? new Shared.Dto.Ontology.ObjectInfomationDto() : await _cacheManager.GetObjectInformation(model.AutoMlSolution)),
                    metrics);
                trainingDto.models.Add(modelDto);
            }

            return trainingDto;
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
                getTrainingRequest.UserId = username;
                getTrainingRequest.TrainingId = request.TrainingId;
                GetTrainingResponse reply = _client.GetTraining(getTrainingRequest);
                Training training = reply.Training;

                TrainingDto trainingDto = await CreateTrainingDtoFromTraining(username, training);
                response = new GetTrainingResponseDto(trainingDto);
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
                deleteTrainingsRequest.TrainingId = request.TrainingId;
                deleteTrainingsRequest.UserId = username;
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
