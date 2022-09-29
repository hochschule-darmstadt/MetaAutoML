using BlazorBoilerplate.Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.User
{
    public class GetHomeOverviewInformationResponseDto
    {
        public int TotalDatasetAmount { get; set; }
        public int TotalTrainingAmount { get; set; }
        public int TotalModelAmount { get; set; }
        public int RunningTrainingAmount { get; set; }
        public GetHomeOverviewInformationResponseDto()
        {

        }
        public GetHomeOverviewInformationResponseDto(GetHomeOverviewInformationResponse information)
        {
            TotalDatasetAmount = information.DatasetAmount;
            TotalModelAmount = information.ModelAmount;
            TotalTrainingAmount = information.TrainingAmount;
            RunningTrainingAmount = information.RunningTrainingAmount;
        }
    }
}
