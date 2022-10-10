using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class GetPredictionsResponseDto
    {
        public List<PredictionDto> Predictions { get; set; }
        public GetPredictionsResponseDto()
        {
            Predictions = new List<PredictionDto>();
        }
        public GetPredictionsResponseDto(Server.GetPredictionsResponse predictions)
        {
            Predictions = new List<PredictionDto>();
            foreach (var item in predictions.Predictions)
            {
                Predictions.Add(new PredictionDto(item));
            }
        }
    }
}
