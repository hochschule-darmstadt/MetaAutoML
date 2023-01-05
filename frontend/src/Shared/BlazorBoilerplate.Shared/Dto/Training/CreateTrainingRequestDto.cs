using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class CreateTrainingRequestDto
    {
        public string DatasetId { get; set; }
        public CreateTrainingConfigurationDto Configuration { get; set; }
        public Dictionary<string, ColumnSchema> Schema { get; set; }
        public CreateTrainingRequestDto()
        {
            Configuration = new CreateTrainingConfigurationDto();
            Schema = new Dictionary<string, ColumnSchema>();
        }
    }
    public class CreateTrainingConfigurationDto
    {

        public string Task { get; set; }
        public string Target { get; set; }
        public List<string> EnabledStrategies { get; set; }
        public int RuntimeLimit { get; set; }
        public string Metric { get; set; }
        public List<string> SelectedAutoMlSolutions { get; set; }
        public List<string> SelecctedMlLibraries { get; set; }
        public CreateTrainingConfigurationDto()
        {
            EnabledStrategies = new List<string>();
            SelecctedMlLibraries = new List<string>();
            SelectedAutoMlSolutions = new List<string>();
        }
    }
}
