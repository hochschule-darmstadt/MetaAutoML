using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingDto
    {
        public string Identifier { get; set; }
        public List<AdapterStatusDto> Adapters { get; set; }
        public string DatasetIdentifier { get; set; }
        public string DatasetName { get; set; }
        public string Task { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public List<ObjectInfomationDto> SelectedMlLibraries { get; set; }
        public List<ObjectInfomationDto> SelectedAutoMls { get; set; }
        public Dictionary<string, dynamic> RuntimeConstraints { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public Dictionary<string, dynamic> TestConfiguration { get; set; }
        public string Status { get; set; }
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public List<StrategyControllerEventDto> Events { get; set; }

        public TrainingDto()
        {
            Adapters = new List<AdapterStatusDto>();
            Configuration = new Dictionary<string, dynamic>();
            SelectedMlLibraries = new List<ObjectInfomationDto>();
            SelectedAutoMls = new List<ObjectInfomationDto>();
            RuntimeConstraints = new Dictionary<string, dynamic>();
            DatasetConfiguration = new Dictionary<string, dynamic>();
            TestConfiguration = new Dictionary<string, dynamic>();
            Events = new List<StrategyControllerEventDto>();

        }
    }
}
