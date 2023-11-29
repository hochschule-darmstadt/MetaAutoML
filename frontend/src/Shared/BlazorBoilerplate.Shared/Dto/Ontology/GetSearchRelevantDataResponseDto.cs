using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetSearchRelevantDataResponseDto
    {
        public List<ObjectInfomationDto> Tasks { get; set; }
        public GetSearchRelevantDataResponseDto(List<ObjectInfomationDto> tasks)
        {
            Tasks = tasks;
        }
    }
}
