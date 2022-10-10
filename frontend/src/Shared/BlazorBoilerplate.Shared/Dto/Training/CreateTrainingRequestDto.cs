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
        public string DatasetId { get; set; }
        public TrainingConfigurationDto Configuration { get; set; }
        public Dictionary<string, dynamic> DatasetConfiguration { get; set; }
        public CreateTrainingRequestDto()
        {
            Configuration = new TrainingConfigurationDto();
            DatasetConfiguration = new Dictionary<string, dynamic>();
        }
    }
}
