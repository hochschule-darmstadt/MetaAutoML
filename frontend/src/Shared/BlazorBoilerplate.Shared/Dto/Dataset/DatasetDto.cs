using Apache.Arrow;
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
        public Dictionary<string, ColumnSchema> Schema { get; set; }
        public DatasetDto()
        {
            Analysis = new Dictionary<string, dynamic>();
        }
        public DatasetDto(GetDatasetResponse grpcObject, ObjectInfomationDto type, Dictionary<string, ColumnSchema> schema)
        {
            Id = grpcObject.Dataset.Id;
            Name = grpcObject.Dataset.Name;
            Type = type;
            FileConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Dataset.FileConfiguration);
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Dataset.Analysis);
            Analysis["creation_date"] = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc).AddSeconds(Analysis["creation_date"]);
            Schema = schema;
        }
        public DatasetDto(Server.Dataset grpcObject, ObjectInfomationDto type, Dictionary<string, ColumnSchema> schema)
        {
            Id = grpcObject.Id;
            Name = grpcObject.Name;
            Type = type;
            FileConfiguration = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.FileConfiguration);
            Analysis = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(grpcObject.Analysis);
            Analysis["creation_date"] = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc).AddSeconds(Analysis["creation_date"]);
            Schema = schema;
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
        public Encoding GetEncoding()
        {
            switch (this.FileConfiguration["encoding"])
            {
                case "utf-8":
                    return Encoding.UTF8;
                case "latin-1":
                    return Encoding.Latin1;
                case "utf-32":
                    return Encoding.UTF32;
                case "utf-16":
                    return Encoding.BigEndianUnicode;
                default:
                    return Encoding.UTF8;
            }
        }
    }
    public class ColumnSchema
    {
        public ColumnSchema(ObjectInfomationDto datatypeDetected, List<ObjectInfomationDto> datatypesCompatible, ObjectInfomationDto datatypeSelected, List<ObjectInfomationDto> rolesCompatible, ObjectInfomationDto roleSelected)
        {
            DatatypeDetected = datatypeDetected;
            DatatypesCompatible = datatypesCompatible;
            DatatypeSelected = datatypeSelected;
            RolesCompatible = rolesCompatible;
            RoleSelected = roleSelected;
        }
        public ObjectInfomationDto DatatypeDetected { get; set; }
        public List<ObjectInfomationDto> DatatypesCompatible { get; set; }
        public ObjectInfomationDto DatatypeSelected { get; set; }
        public List<ObjectInfomationDto> RolesCompatible { get; set; }
        public ObjectInfomationDto RoleSelected { get; set; }
    }
}
