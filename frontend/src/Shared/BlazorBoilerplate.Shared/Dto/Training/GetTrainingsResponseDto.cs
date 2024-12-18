using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingsResponseDto
    {
        public List<TrainingMetaDataDto> Trainings { get; set; }
        public PaginationMetadataDto PaginationMetadata { get; set; }
        public GetTrainingsResponseDto()
        {
            Trainings = new List<TrainingMetaDataDto>();
        }
    }

    public class PaginationMetadataDto
    {
        public int TotalItems { get; set; }
        public int PageNumber { get; set; }
        public int PageSize { get; set; }
        public int TotalPages { get; set; }
    }
}
