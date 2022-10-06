using BlazorBoilerplate.Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.PredictionDataset
{
    public class PredictionDto
    {
        public DateTime CreationTime { get; set; }
        public string Status { get; set; }
        public string PredictionPath { get; set; }
        public float PredictionTime { get; set; }
        public PredictionDto()
        {

        }
        public PredictionDto(Prediction prediction)
        {
            CreationTime = prediction.CreationTime.ToDateTime();
            Status = prediction.Status;
            PredictionPath = prediction.PredictionPath;
            PredictionTime = prediction.PredictionTime;
        }
    }
}
