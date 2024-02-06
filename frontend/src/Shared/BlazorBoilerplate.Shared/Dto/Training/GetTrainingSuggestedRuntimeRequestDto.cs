using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingSuggestedRuntimeRequestDto
    {
        public string DatasetId { get; set; }

        public string Task {  get; set; }
    }
}
