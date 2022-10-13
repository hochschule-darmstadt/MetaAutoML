using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingsResponseDto
    {
        public List<TrainingDto> Trainings { get; set; }
        public GetTrainingsResponseDto()
        {
            Trainings = new List<TrainingDto>();
        }
    }
}
