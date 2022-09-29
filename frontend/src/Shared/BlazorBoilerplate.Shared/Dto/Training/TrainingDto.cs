using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingDto
    {
        public string Identifier { get; set; }
        public List<ModelDto> models { get; set; }
        public string DatasetIdentifier { get; set; }
        public string DatasetName { get; set; }
        public ObjectInfomationDto Task { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public List<ObjectInfomationDto> SelectedMlLibraries { get; set; }
        public List<ObjectInfomationDto> SelectedAutoMls { get; set; }
        public Dictionary<string, dynamic> RuntimeConstraints { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public Dictionary<string, dynamic> TestConfiguration { get; set; }
        public string Status { get; set; }
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public List<StrategyControllerEventDto> Events { get; set; }

        public TrainingDto()
        {

        }
        public TrainingDto(Server.Training grpcResponse, ObjectInfomationDto task)
        {
            Identifier = grpcResponse.Identifier;
            models = new List<ModelDto>();
            DatasetIdentifier = grpcResponse.DatasetIdentifier;
            DatasetName = grpcResponse.DatasetName;
            Task = task;
            Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcResponse.Configuration);
            SelectedMlLibraries = new List<ObjectInfomationDto>();
            SelectedAutoMls = new List<ObjectInfomationDto>();
            RuntimeConstraints = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcResponse.RuntimeConstraints);
            DatasetConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcResponse.DatasetConfiguration);
            TestConfiguration = new Dictionary<string, dynamic>();
            Status = grpcResponse.Status;
            StartTime = grpcResponse.StartTime.ToDateTime();
            EndTime = grpcResponse.EndTime.ToDateTime();
            Events = new List<StrategyControllerEventDto>();
            foreach (var trainingEvent in grpcResponse.Events)
            {
                var strategyControllerEvent = new StrategyControllerEventDto
                {
                    Type = trainingEvent.Type,
                    Meta = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(trainingEvent.Meta),
                    Timestamp = trainingEvent.Timestamp.ToDateTime()
                };
               Events.Add(strategyControllerEvent);
            }
        }
    }
}
