using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class StrategyControllerStrategyDto
    {
        public string ID { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
    }

    public class GetAvailableStrategiesResponseDto
    {
        public List<StrategyControllerStrategyDto> Strategies { get; set; }
    }
}
