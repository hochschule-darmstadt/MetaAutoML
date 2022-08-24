using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class GetModelExplanationRequestDto
    {
        public string ModelIdentifier { get; set; }
        public bool GetShortPreview { get; set; }
    }
}
