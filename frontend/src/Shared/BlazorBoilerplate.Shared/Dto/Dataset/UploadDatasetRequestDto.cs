using BlazorBoilerplate.Shared.Interfaces;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class UploadDatasetRequestDto
    {
        public string FileNameOrURL { get; set; }
        public string DatasetName { get; set; }
        public string DatasetType { get; set; }
        public string FileSource { get; set; }
        public byte[] Content { get; set; }
        public int ChunkNumber { get; set; }
        public int TotalChunkNumber { get; set; }
    }
}
