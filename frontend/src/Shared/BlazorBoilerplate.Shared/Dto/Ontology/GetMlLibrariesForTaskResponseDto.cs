using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetMlLibrariesForTaskResponseDto
    {
        public List<ObjectInfomationDto> MlLibraries { get; set; }
        public GetMlLibrariesForTaskResponseDto(List<ObjectInfomationDto> mlLibraries)
        {
            MlLibraries = mlLibraries;
        }
    }
}
