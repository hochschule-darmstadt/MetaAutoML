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
        public Dictionary<string, ColumnSchemaDto> Schema { get; set; }
        public bool SaveSchema { get; set; }
        public bool PerformModelAnalysis { get; set; } = true;
        public CreateTrainingRequestDto()
        {
            Configuration = new CreateTrainingConfigurationDto();
            Schema = new Dictionary<string, ColumnSchemaDto>();
            SaveSchema = true;
        }
    }
    public class CreateTrainingConfigurationDto
    {

        public string Task { get; set; }
        public List<string> EnabledStrategies { get; set; } = new();
        public int RuntimeLimit { get; set; }
        public string Metric { get; set; }
        public List<string> SelectedAutoMlSolutions { get; set; } = new();
        public List<string> SelecctedMlLibraries { get; set; } = new();
        public List<ParameterDto> Parameters { get; set; } = new();
    }

    public class ParameterDto
    {
        public string Iri { get; set; }
        public List<string> Values { get; set; }
    }
}
