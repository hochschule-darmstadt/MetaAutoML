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
        public void ConvertColumnsToRows()
        {
            for (int b = 0; b < Columns[0].FirstEntries.Count; b++)
            {
                List<string> row = new List<string>();
                for (int i = 0; i < Columns.Count; i++)
                {
                    row.Add(Columns[i].FirstEntries[b]);
                }
                RowContent.Add(row);
            }
        }
    }

    public class ColumnsDto
    {

        public string Name { get; set; }
        public Server.DataType Type { get; set; }
        public List<Server.DataType> ConvertibleTypes { get; set; }
        public List<string> FirstEntries { get; set; }
    }
}
