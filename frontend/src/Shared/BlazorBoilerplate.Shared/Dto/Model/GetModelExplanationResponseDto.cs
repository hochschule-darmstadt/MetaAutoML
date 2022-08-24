using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class GetModelExplanationResponseDto
    {
        public string Status { get; set; }
        public string Detail { get; set; }
        public List<ModelExplanation> Analyses { get; set; } = new List<ModelExplanation>();
    }
    public class ModelExplanation
    {
        public string Type { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public byte[] Content { get; set; }
    }
}
