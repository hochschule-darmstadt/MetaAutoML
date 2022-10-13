using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class TrainingConfigurationDto
    {
        public ObjectInfomationDto Task { get; set; }
        public string Target { get; set; }
        public List<string> EnabledStrategies { get; set; }
        public int RuntimeLimit { get; set; }
        public ObjectInfomationDto Metric { get; set; }
        public List<ObjectInfomationDto> SelectedAutoMlSolutions { get; set; }
        public List<ObjectInfomationDto> SelecctedMlLibraries { get; set; }
        public TrainingConfigurationDto()
        {
            EnabledStrategies = new List<string>();
            SelecctedMlLibraries = new List<ObjectInfomationDto>();
            SelectedAutoMlSolutions = new List<ObjectInfomationDto>();
        }
    }
}
