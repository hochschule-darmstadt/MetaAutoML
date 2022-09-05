using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class GetDatasetAnalysisResponseDto
    {
        public List<DatasetAnalysisCategory> AnalysisCategories { get; set; } = new List<DatasetAnalysisCategory>();
    }
    public class DatasetAnalysisCategory
    {
        public string CategoryTitle { get; set; }
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
