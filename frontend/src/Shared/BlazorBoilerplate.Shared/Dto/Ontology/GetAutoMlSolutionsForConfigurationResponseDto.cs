using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetAutoMlSolutionsForConfigurationResponseDto
    {
        public List<ObjectInfomationDto> AutoMlSolutions { get; set; }
        public GetAutoMlSolutionsForConfigurationResponseDto(List<ObjectInfomationDto> automlSolutions)
        {
            AutoMlSolutions = automlSolutions;
        }
    }
}
