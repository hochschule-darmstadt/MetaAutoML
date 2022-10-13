using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class DownloadModelResponseDto
    {
        public string Name { get; set; }
        public byte[] Content { get; set; }
    }
}
