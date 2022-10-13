using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class StrategyControllerEventDto
    {
        public string Type { get; set; }
        public Dictionary<string, dynamic> Meta { get; set; }
        public DateTime Timestamp { get; set; }

        public StrategyControllerEventDto()
        {
            Meta = new Dictionary<string, dynamic>();
        }
    }
}
