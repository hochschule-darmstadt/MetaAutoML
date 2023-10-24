using BlazorBoilerplate.Server;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.Dynamic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingEventDto
    {
        public string Type { get; set; }
        public Dictionary<string, Object> Meta { get; set; }
        public DateTime Timestamp { get; set; }
        public TrainingEventDto()
        {
            Meta = new Dictionary<string, object>();
        }
        public TrainingEventDto(Server.StrategyControllerEvent controllerEvent)
        {
            try
            {
                Type = controllerEvent.Type;
                var expConverter = new ExpandoObjectConverter();
                Meta = new Dictionary<string, Object>(JsonConvert.DeserializeObject<ExpandoObject>(controllerEvent.Meta, expConverter));
                Timestamp = controllerEvent.Timestamp.ToDateTime();
            }
            catch (Exception ex)
            { Console.WriteLine(ex); }
         
        }
    }
}
