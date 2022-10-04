using BlazorBoilerplate.Server;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.PredictionDataset
{
    public class PredictionDatasetDto
    {
        public string Identifier { get; set; }
        public string Name { get; set; }
        public ObjectInfomationDto Type { get; set; }
        public DateTime Creation_date { get; set; }
        public long Size { get; set; }
        public Dictionary<string, dynamic> Analysis { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public PredictionDatasetDto()
        {
            Analysis = new Dictionary<string, dynamic>();
        }
        public PredictionDatasetDto(GetPredictionDatasetResponse grpcObject, ObjectInfomationDto type)
        {
            Identifier = grpcObject.PredictionDataset.Identifier;
            Name = grpcObject.PredictionDataset.Name;
            Type = type;
            Creation_date = grpcObject.PredictionDataset.CreationDate.ToDateTime();
            Size = grpcObject.PredictionDataset.Size;
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.PredictionDataset.Analysis);
            Configuration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.PredictionDataset.FileConfiguration);
        }
        public PredictionDatasetDto(Server.PredictionDataset grpcObject, ObjectInfomationDto type)
        {
            Identifier = grpcObject.Identifier;
            Name = grpcObject.Name;
            Type = type;
            Creation_date = grpcObject.CreationDate.ToDateTime();
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
