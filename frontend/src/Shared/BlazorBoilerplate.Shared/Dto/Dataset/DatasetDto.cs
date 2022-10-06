using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class DatasetDto
    {
        public string Identifier { get; set; }
        public string Name { get; set; }
        public ObjectInfomationDto Type { get; set; }
        public DateTime CreationTime { get; set; }
        public long Size { get; set; }
        public Dictionary<string, dynamic> Analysis { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public DatasetDto()
        {
            Analysis = new Dictionary<string, dynamic>();
        }
        public DatasetDto(GetDatasetResponse grpcObject, ObjectInfomationDto type)
        {
            Identifier = grpcObject.Dataset.Identifier;
            Name = grpcObject.Dataset.Name;
            Type = type;
            CreationTime = grpcObject.Dataset.CreationTime.ToDateTime();
            Size = grpcObject.Dataset.Size;
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Dataset.Analysis);
            Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Dataset.FileConfiguration);
        }
        public DatasetDto(Server.Dataset grpcObject, ObjectInfomationDto type)
        {
            Identifier = grpcObject.Identifier;
            Name = grpcObject.Name;
            Type = type;
            CreationTime = grpcObject.CreationTime.ToDateTime();
            Size = grpcObject.Size;
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Analysis);
            Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.FileConfiguration);
        }

        public char GetDelimiter()
        {
            switch (this.Configuration["delimiter"])
            {
                case "comma":
                    return ',';
                case "semicolon":
                    return ';';
                case "space":
                    return ' ';
                case "tab":
                    return '\t';
                default:
                    return ',';
            }
        }
        public string GetDelimiterStr()
        {
            switch (this.Configuration["delimiter"])
            {
                case "comma":
                    return ",";
                case "semicolon":
                    return ";";
                case "space":
                    return " ";
                case "tab":
                    return "\t";
                default:
                    return ",";
            }
        }
    }
}
