using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.PredictionDataset
{
    public class GetPredictionDatasetPredictionResponseDto
    {
        public string Name { get; set; }
        public byte[] Content { get; set; }
    }
}
