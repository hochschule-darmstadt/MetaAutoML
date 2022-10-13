using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingRuntimeProfileDto
    {
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public List<TrainingEventDto> Events { get; set; }
        public TrainingRuntimeProfileDto()
        {
            Events = new List<TrainingEventDto>();
        }
        public TrainingRuntimeProfileDto(Server.TrainingRuntimeProfile runtime)
        {
            StartTime = runtime.StartTime.ToDateTime();
            EndTime = runtime.EndTime.ToDateTime();
            Events = new List<TrainingEventDto>();
            foreach (var item in runtime.Events)
            {
                Events.Add(new TrainingEventDto(item));
            }
        }
    }
}
