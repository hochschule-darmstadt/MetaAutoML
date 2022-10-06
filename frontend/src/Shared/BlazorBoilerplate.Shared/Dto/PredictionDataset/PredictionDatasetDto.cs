using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.PredictionDataset
{
    public class PredictionDatasetDto
    {
        public string Identifier { get; set; }
        public string Name { get; set; }
        public ObjectInfomationDto Type { get; set; }
        public DateTime Creation_date { get; set; }
        public long Size { get; set; }
        public Dictionary<string, ModelPredictionsDto> Predictions { get; set; }
        public PredictionDatasetDto()
        {
            Predictions = new Dictionary<string, ModelPredictionsDto>();
        }
        public PredictionDatasetDto(GetPredictionDatasetResponse grpcObject, ObjectInfomationDto type)
        {
            Identifier = grpcObject.PredictionDataset.Identifier;
            Name = grpcObject.PredictionDataset.Name;
            Type = type;
            Creation_date = grpcObject.PredictionDataset.CreationTime.ToDateTime();
            Size = grpcObject.PredictionDataset.Size;
            Predictions = new Dictionary<string, ModelPredictionsDto>();
            foreach (var item in grpcObject.PredictionDataset.Predictions)
            {
                Predictions.Add(item.Key, new ModelPredictionsDto(item.Value));
            }
        }
        public PredictionDatasetDto(Server.PredictionDataset grpcObject, ObjectInfomationDto type)
        {
            Identifier = grpcObject.Identifier;
            Name = grpcObject.Name;
            Type = type;
            Creation_date = grpcObject.CreationTime.ToDateTime();
            Size = grpcObject.Size;
            Predictions = new Dictionary<string, ModelPredictionsDto>();
            foreach (var item in grpcObject.Predictions)
            {
                Predictions.Add(item.Key, new ModelPredictionsDto(item.Value));
            }
        }
    }
}
