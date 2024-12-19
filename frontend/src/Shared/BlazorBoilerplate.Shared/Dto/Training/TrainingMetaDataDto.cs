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
    public class TrainingMetaDataDto
    {
        public string Id { get; set; }
        public string DatasetId { get; set; }
        public string DatasetName { get; set; }
        public ObjectInfomationDto Task { get; set; }
        public string Status { get; set; }
        public DateTime StartTime { get; set; }
        public TrainingMetaDataDto()
        {

        }
        public TrainingMetaDataDto(Server.TrainingMetaData grpcResponse, string datasetName)
        {
            Id = grpcResponse.Id;
            DatasetId = grpcResponse.DatasetId;
            DatasetName = datasetName;
            Status = grpcResponse.Status;
            StartTime = grpcResponse.StartTime.ToDateTime();
        }
    }
}
