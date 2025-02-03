using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetRequestDto
    {
        public string DatasetId { get; set; }
        public bool Short { get; set; } = true;
    }
}
