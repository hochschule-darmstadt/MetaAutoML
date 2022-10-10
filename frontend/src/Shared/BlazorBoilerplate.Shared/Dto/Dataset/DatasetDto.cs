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
        public string Id { get; set; }
        public string Name { get; set; }
        public ObjectInfomationDto Type { get; set; }
        public Dictionary<string, dynamic> FileConfiguration { get; set; }
        public Dictionary<string, dynamic> Analysis { get; set; }
        public DatasetDto()
        {
            Analysis = new Dictionary<string, dynamic>();
        }
        public DatasetDto(GetDatasetResponse grpcObject, ObjectInfomationDto type)
        {
            Id = grpcObject.Dataset.Id;
            Name = grpcObject.Dataset.Name;
            Type = type;
            FileConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Dataset.FileConfiguration);
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Dataset.Analysis);
        }
        public DatasetDto(Server.Dataset grpcObject, ObjectInfomationDto type)
        {
            Id = grpcObject.Id;
            Name = grpcObject.Name;
            Type = type;
            FileConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.FileConfiguration);
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Analysis);
            Analysis["creation_date"] = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc).AddSeconds(Analysis["creation_date"]);
        }

        public char GetDelimiter()
        {
            switch (this.FileConfiguration["delimiter"])
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
            switch (this.FileConfiguration["delimiter"])
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
