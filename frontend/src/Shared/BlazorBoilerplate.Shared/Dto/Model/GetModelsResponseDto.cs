using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class GetModelsResponseDto
    {
        public List<ModelDto> Models { get; set; }
        public GetModelsResponseDto()
        {
            Models = new List<ModelDto>();
        }
    }
}
