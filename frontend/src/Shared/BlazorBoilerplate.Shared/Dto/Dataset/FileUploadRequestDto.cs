using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class FileUploadRequestDto
    {
        public string FileName { get; set; }
        public string DatasetName { get; set; }
        public string Content { get; set; }
        public string DatasetType { get; set; }
    }
}
