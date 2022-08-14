using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetAllTrainingsResponseDto
    {
        public List<GetTrainingResponseDto> Trainings { get; set; }
        public GetAllTrainingsResponseDto()
        {
            Trainings = new List<GetTrainingResponseDto>();
        }
    }
}
