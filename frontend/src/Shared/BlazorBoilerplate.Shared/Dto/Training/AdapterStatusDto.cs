using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class AdapterStatusDto
    {
        public int Identifier { get; set; }
        public string Name { get; set; }
        public string Status { get; set; }
        public List<string> Messages { get; set; }
        public float TestScore { get; set; }
        public int Runtime { get; set; }
        public float PredictionTime { get; set; }
        public string Library { get; set; }
        public string Model { get; set; }

        public AdapterStatusDto()
        {
            Messages = new List<string>();
        }
    }
}
