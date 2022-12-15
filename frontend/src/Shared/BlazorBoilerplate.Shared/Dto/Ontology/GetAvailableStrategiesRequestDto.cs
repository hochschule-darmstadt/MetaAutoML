using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetAvailableStrategiesRequestDto
    {
        public Dictionary<string, string> Configuration { get; set; }
        public String DatasetId { get; set; }
    }
}
