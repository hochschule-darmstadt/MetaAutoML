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
        public string SignalrConnectionId { get; set; }
        public IFormFile File { get; set; }
        public string Url { get; set; }
        public string DatasetName { get; set; }
        public string DatasetType { get; set; }

    }
}
