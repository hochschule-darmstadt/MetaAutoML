using BlazorBoilerplate.Server;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetTabularDatasetColumnResponseDto
    {
        public List<List<string>> RowContent { get; set; }
        public List<ColumnsDto> Columns { get; set; }
        public GetTabularDatasetColumnResponseDto()
        {
            Columns = new List<ColumnsDto>();
            RowContent = new List<List<string>>();
        }
    }

    public class ColumnsDto
    {

        public string Name { get; set; }
        public Server.DataType Type { get; set; }
        public List<Server.DataType> ConvertibleTypes { get; set; }
    }
}
