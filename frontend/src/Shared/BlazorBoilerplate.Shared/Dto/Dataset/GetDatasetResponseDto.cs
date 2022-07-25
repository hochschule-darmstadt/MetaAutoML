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
        public int? Columns { get; set; }
        public int? Rows { get; set; }
        public DateTime Creation_date { get; set; }
        public string Identifier { get; set; }
        public GetDatasetResponseDto(string name, ObjectInfomationDto type, int columns, int rows, DateTime time, string identifier)
        {
            Name = name;
            Type = type;
            Columns = columns;
            Rows = rows;
            Creation_date = time;
            Identifier = identifier;
        }
    }
}
