using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class DownloadPredictionResponseDto
    {
        public string Name { get; set; }
        public byte[] Content { get; set; }
    }
}
