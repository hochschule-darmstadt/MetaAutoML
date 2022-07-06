using BlazorBoilerplate.Shared.Dto.AutoML;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Session
{
    public class GetSessionResponseDto
    {
        public string Status { get; set; }
        public List<AutoMLStatusDto> AutoMls { get; set; }
        public string DatasetId { get; set; }
        public string DatasetName { get; set; }
        public string Task { get; set; }
        public List<String> RequiredMlLibraries { get; set; }
        public List<String> RequiredAutoMLs { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public Dictionary<string, dynamic> RuntimeConstraints { get; set; }
        public Dictionary<string, dynamic> FileConfiguration { get; set; }
        public Dictionary<string, dynamic> TestConfiguration { get; set; }

        public GetSessionResponseDto()
        {
            AutoMls = new List<AutoMLStatusDto>();
            RequiredMlLibraries = new List<String>();
            RequiredAutoMLs = new List<String>();
            DatasetConfiguration = new Dictionary<string, dynamic>();
            Configuration = new Dictionary<string, dynamic>();
            RuntimeConstraints = new Dictionary<string, dynamic>();
            FileConfiguration = new Dictionary<string, dynamic>();
            TestConfiguration = new Dictionary<string, dynamic>();
        }
    }
}
