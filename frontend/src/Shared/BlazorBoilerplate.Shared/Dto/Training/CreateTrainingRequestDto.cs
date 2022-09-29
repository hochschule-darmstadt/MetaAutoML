using BlazorBoilerplate.Shared.Dto.Dataset;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class CreateTrainingRequestDto
    {
        public string DatasetIdentifier { get; set; }
        public string Task { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public List<string> SelectedAutoMLs { get; set; }
        public Dictionary<string, dynamic> RuntimeConstraints { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public Dictionary<string, dynamic> TestConfiguration { get; set; }
        public string Metric { get; set; }
        public List<string> SelectedMlLibraries { get; set; }
        public CreateTrainingRequestDto()
        {
            Configuration = new Dictionary<string, dynamic>();
            SelectedAutoMLs = new List<string>();
            RuntimeConstraints = new Dictionary<string, dynamic>();
            DatasetConfiguration = new Dictionary<string, dynamic>();
            TestConfiguration = new Dictionary<string, dynamic>();
            SelectedMlLibraries = new List<string>();
        }
    }
}
