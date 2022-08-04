using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetPreviewResponseDto
    {
        public dynamic DatasetPreview { get; set; }
    }
    public class ImagePreviewDto
    {
        public string FileType { get; set; }
        public string FolderType { get; set; }
        public byte[] Content { get; set; }
    }
}
