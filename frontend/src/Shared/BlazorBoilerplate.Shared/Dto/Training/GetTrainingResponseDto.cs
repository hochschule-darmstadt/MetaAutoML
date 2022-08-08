using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingResponseDto
    {
        public string ID { get; set; }
        public DateTime StartTime { get; set; }
        public string Status { get; set; }
        public List<AutoMLStatusDto> AutoMls { get; set; }
        public string DatasetId { get; set; }
        public string DatasetName { get; set; }
        public ObjectInfomationDto Task { get; set; }
        public List<ObjectInfomationDto> RequiredMlLibraries { get; set; }
        public List<ObjectInfomationDto> RequiredAutoMLs { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public Dictionary<string, dynamic> RuntimeConstraints { get; set; }
        public Dictionary<string, dynamic> FileConfiguration { get; set; }
        public Dictionary<string, dynamic> TestConfiguration { get; set; }
        public bool ShowDetails { get; set; }

        public GetTrainingResponseDto()
        {
            AutoMls = new List<AutoMLStatusDto>();
            RequiredMlLibraries = new List<ObjectInfomationDto>();
            RequiredAutoMLs = new List<ObjectInfomationDto>();
            DatasetConfiguration = new Dictionary<string, dynamic>();
            Configuration = new Dictionary<string, dynamic>();
            RuntimeConstraints = new Dictionary<string, dynamic>();
            FileConfiguration = new Dictionary<string, dynamic>();
            TestConfiguration = new Dictionary<string, dynamic>();
            ShowDetails = false;
        }
    }
}
