using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingIdsResponseDto
    {
        public List<string> TrainingIds { get; set; }
        public GetTrainingIdsResponseDto()
        {
            TrainingIds = new List<string>();
        }
    }
}
