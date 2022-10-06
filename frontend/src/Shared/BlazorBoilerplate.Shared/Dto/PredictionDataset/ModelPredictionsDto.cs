using BlazorBoilerplate.Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.PredictionDataset
{
    public class ModelPredictionsDto
    {
        public Dictionary<string, PredictionDto> Predictions { get; set; }
        public ModelPredictionsDto()
        {
            Predictions = new Dictionary<string, PredictionDto>();
        }
        public ModelPredictionsDto(ModelPrediction modelPrediction)
        {
            Predictions = new Dictionary<string, PredictionDto>();
            foreach (var item in modelPrediction.Predictions)
            {
                Predictions.Add(item.Key, new PredictionDto(item.Value));
            }
        }
    }
}
