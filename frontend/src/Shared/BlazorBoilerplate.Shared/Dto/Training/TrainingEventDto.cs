using BlazorBoilerplate.Server;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingEventDto
    {
        public string Type { get; set; }
        public Dictionary<string, string> Meta { get; set; }
        public DateTime Timestamp { get; set; }
        public TrainingEventDto()
        {
            Meta = new Dictionary<string, string>();
        }
        public TrainingEventDto(Server.StrategyControllerEvent controllerEvent)
        {
            Type = controllerEvent.Type;
            Meta = JsonConvert.DeserializeObject<Dictionary<string, string>>(controllerEvent.Meta);
            Timestamp = controllerEvent.Timestamp.ToDateTime();
        }
    }
}
