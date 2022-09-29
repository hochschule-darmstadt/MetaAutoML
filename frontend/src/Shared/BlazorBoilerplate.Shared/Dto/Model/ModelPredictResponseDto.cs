using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class ModelPredictResponseDto
    {
        public List<string> Predictions { get; set; }
        public double Predictiontime { get; set; }
        public ModelPredictResponseDto()
        {
            Predictions = new List<string>();
        }
    }
}
