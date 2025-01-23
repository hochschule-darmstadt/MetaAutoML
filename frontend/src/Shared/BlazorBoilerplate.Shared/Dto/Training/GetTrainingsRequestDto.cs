using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Training
{
    public class GetTrainingsRequestDto
    {
        public bool Short { get; set; } = false;
        public bool Pagination { get; set; } = false;
        public int PageNumber { get; set; } = 1; //Pagination page always 1 based
        public int PageSize { get; set; } = 10;
        public bool OnlyLastDay { get; set; } = false;
        public string SearchString { get; set; }
        public string SortDirection { get; set; }
        public string SortLabel { get; set; }
    }
}
