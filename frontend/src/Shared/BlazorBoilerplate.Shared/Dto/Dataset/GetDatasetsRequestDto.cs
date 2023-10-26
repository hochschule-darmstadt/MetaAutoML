using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetsRequestDto
    {
        public bool OnlyFiveRecent { get; set; } = false;
        public bool Pagination { get; set; } = false;
        public int PageNumber { get; set; } = 1; //Pagination page always 1 based
    }
}
