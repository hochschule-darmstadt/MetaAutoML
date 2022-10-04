using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.PredictionDataset
{
    public class GetPredictionDatasetsResponseDto
    {
        public List<PredictionDatasetDto> Datasets { get; set; }
        public GetPredictionDatasetsResponseDto()
        {
            Datasets = new List<PredictionDatasetDto>();
        }
    }
}
