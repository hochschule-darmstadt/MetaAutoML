using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingDto
    {
        public string Id { get; set; }
        public string DatasetId { get; set; }
        public string DatasetName { get; set; }
        public List<ModelDto> models { get; set; }
        public TrainingConfigurationDto Configuration { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public string Status { get; set; }
        public TrainingRuntimeProfileDto RuntimeProfile { get; set; }
        public TrainingDto()
        {

        }
        public TrainingDto(Server.Training grpcResponse, string datasetName)
        {
            Id = grpcResponse.Id;
            DatasetId = grpcResponse.DatasetId;
            DatasetName = datasetName;
            models = new List<ModelDto>();
            Configuration = new TrainingConfigurationDto();
            DatasetConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcResponse.DatasetConfiguration);
            Status = grpcResponse.Status;
            RuntimeProfile = new TrainingRuntimeProfileDto(grpcResponse.RuntimeProfile);
        }
    }
}
