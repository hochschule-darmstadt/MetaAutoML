using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetsResponseDto
    {
        public List<GetDatasetResponseDto> Datasets { get; set; }
        public GetDatasetsResponseDto()
        {
            Datasets = new List<GetDatasetResponseDto>();
        }
    }
}
