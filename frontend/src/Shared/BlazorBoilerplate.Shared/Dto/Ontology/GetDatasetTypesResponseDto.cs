using BlazorBoilerplate.Constants;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetDatasetTypesResponseDto
    {
        public List<ObjectInfomationDto> DatasetTypes { get; set; } = new List<ObjectInfomationDto>();
    }
}