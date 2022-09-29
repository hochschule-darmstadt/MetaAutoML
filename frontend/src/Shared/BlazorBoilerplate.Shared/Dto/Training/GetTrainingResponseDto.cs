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
        public TrainingDto Training { get; set; }
        public GetTrainingResponseDto(TrainingDto training)
        {
            Training = training;
        }
    }
}
