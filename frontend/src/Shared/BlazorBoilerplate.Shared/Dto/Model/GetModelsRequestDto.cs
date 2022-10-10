using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class GetModelsRequestDto
    {
        public string DatasetId { get; set; }
        public bool Top3 { get; set; }
    }
}
