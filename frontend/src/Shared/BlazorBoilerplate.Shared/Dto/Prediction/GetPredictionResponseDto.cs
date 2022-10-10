using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class GetPredictionResponseDto
    {
        public PredictionDto Prediction { get; set; }
        public GetPredictionResponseDto()
        {

        }
        public GetPredictionResponseDto(Server.GetPredictionResponse prediction)
        {
            Prediction = new PredictionDto(prediction.Prediction);
        }
    }
}
