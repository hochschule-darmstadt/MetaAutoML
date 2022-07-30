using BlazorBoilerplate.Constants;
using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetResponseDto
    {
        public string Name { get; set; }
        public ObjectInfomationDto Type { get; set; }
        public long Size { get; set; }
        public DateTime Creation_date { get; set; }
        public string Identifier { get; set; }
        public Dictionary<string, dynamic> Analysis { get; set; }
    }
}
