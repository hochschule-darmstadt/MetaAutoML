using BlazorBoilerplate.Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class StrategyControllerStrategyDto
    {
        public string Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public StrategyControllerStrategyDto()
        {

        }
        public StrategyControllerStrategyDto(Strategy strategy)
        {
            Id = strategy.Id;
            Title = strategy.Title;
            Description = strategy.Description;
        }
    }

    public class GetAvailableStrategiesResponseDto
    {
        public List<StrategyControllerStrategyDto> Strategies { get; set; }
    }
}
