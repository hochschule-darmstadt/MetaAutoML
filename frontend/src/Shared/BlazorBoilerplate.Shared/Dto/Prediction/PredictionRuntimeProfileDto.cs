using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class PredictionRuntimeProfileDto
    {
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public PredictionRuntimeProfileDto()
        {

        }
        public PredictionRuntimeProfileDto(Server.PredictionRuntimeProfile runtime)
        {
            StartTime = runtime.StartTime.ToDateTime();
            EndTime = runtime.EndTime.ToDateTime();
        }
    }
}
