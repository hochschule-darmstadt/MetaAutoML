using BlazorBoilerplate.Shared.Interfaces;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Prediction
{
    public class UploadPredictionRequestDto
    {
        public string FileName { get; set; }
        public string ModelId { get; set; }
        public byte[] Content { get; set; }
        public int ChunkNumber { get; set; }
        public int TotalChunkNumber { get; set; }
    }
}
