using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class CreateTrainingResponseDto
    {
        public string TrainingIdentifier { get; set; }
        public CreateTrainingResponseDto(string trainingIdentifier)
        {
            TrainingIdentifier = trainingIdentifier;
        }
    }
}
