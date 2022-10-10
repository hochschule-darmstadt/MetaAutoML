using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class GetPredictionPreviewResponseDto
    {
        public dynamic DatasetPreview { get; set; }
    }
    public class PredictionImagePreviewDto
    {
        public string FileType { get; set; }
        public string FolderType { get; set; }
        public byte[] Content { get; set; }
    }
}
