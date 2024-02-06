using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BlazorBoilerplate.Server;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetSearchRelevantDataResponseDto
    {
        public List<SearchRelevantData> SearchData { get; set; }
        public GetSearchRelevantDataResponseDto(List<SearchRelevantData> searchData)
        {
            SearchData = searchData;
        }
    }
}
