using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetAnalysisResponseDto
    {
        public List<DatasetAnalysis> Analyses { get; set; } = new List<DatasetAnalysis>();
    }
    public class DatasetAnalysis
    {
        public string Type { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public byte[] Content { get; set; }
    }
}
