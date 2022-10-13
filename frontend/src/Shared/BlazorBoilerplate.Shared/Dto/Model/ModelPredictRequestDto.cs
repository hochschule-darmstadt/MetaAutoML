using BlazorBoilerplate.Shared.Dto.Prediction;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class ModelPredictionRequestDto
    {
        public string PredictionDatasetIdentifier { get; set; }
        public string ModelIdentifier { get; set; }
    }
}