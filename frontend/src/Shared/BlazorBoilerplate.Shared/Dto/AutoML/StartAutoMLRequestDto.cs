using BlazorBoilerplate.Shared.Dto.Dataset;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.AutoML
{
    public class StartAutoMLRequestDto
    {
        public string DatasetIdentifier { get; set; }
        public string DatasetType { get; set; }
        public string Task { get; set; }
        public List<String> RequiredMlLibraries { get; set; }
        public List<String> RequiredAutoMLs { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public Dictionary<string, dynamic> RuntimeConstraints { get; set; }
        public Dictionary<string, dynamic> TestConfig { get; set; }
        public Dictionary<string, dynamic> FileConfiguration { get; set; }
        public StartAutoMLRequestDto()
        {
            RequiredAutoMLs = new List<string>();
            DatasetConfiguration = new Dictionary<string, dynamic>();
            Configuration = new Dictionary<string, dynamic>();
            RuntimeConstraints = new Dictionary<string, dynamic>();
            TestConfig = new Dictionary<string, dynamic>();
            FileConfiguration = new Dictionary<string, dynamic>();
        }
    }
}
