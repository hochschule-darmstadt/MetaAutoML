using BlazorBoilerplate.Constants;
using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetResponseDto
    {
        public DatasetDto Dataset { get; set; }
        public GetDatasetResponseDto(DatasetDto dataset)
        {
            Dataset = dataset;
        }
    }
}
