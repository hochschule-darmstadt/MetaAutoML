using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.General
{
    public class GetHomeOverviewInformationResponseDto
    {
        public int TotalDatasetAmount { get; set; }
        public int TotalTrainingAmount { get; set; }
        public int TotalModelAmount { get; set; }
        public int RunningTrainingAmount { get; set; }
    }
}
