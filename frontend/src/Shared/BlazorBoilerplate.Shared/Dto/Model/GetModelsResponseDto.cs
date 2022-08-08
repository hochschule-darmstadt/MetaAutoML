using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class GetModelsResponseDto
    {
        public List<ModelDto> Models { get; set; }
        public GetModelsResponseDto()
        {
            Models = new List<ModelDto>();
        }
    }

    public class ModelDto
    {
        public string ID { get; set; }
        public string Name { get; set; }
        public string Library { get; set; }
        public string Model { get; set; }
        public string Status { get; set; }
        public List<string> Messages { get; set; }
        public double TestScore { get; set; }
        public double ValidationScore { get; set; }
        public double Predictiontime { get; set; }
        public int Runtime { get; set; }
        public string DatasetId { get; set; }
        public string TrainingId { get; set; }

        public ModelDto()
        {
            Messages = new List<string>();
        }
    }
}
