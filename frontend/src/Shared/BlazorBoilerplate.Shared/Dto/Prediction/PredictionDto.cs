using BlazorBoilerplate.Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class PredictionDto
    {
        public string Id { get; set; }
        public string ModelId { get; set; }
        public string LiveDatasetName { get; set; }
        public string Status { get; set; }
        public PredictionRuntimeProfileDto RuntimeProfile { get; set; }
        public PredictionDto()
        {

        }
        public PredictionDto(Server.Prediction prediction)
        {
            Id = prediction.Id;
            ModelId = prediction.ModelId;
            LiveDatasetName = Path.GetFileName(prediction.LiveDatasetPath);
            Status = prediction.Status;
            RuntimeProfile = new PredictionRuntimeProfileDto(prediction.RuntimeProfile);
        }
    }
}
