using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetDatasetCompatibleTasksRequestDto
    {
        public string DatasetIdentifier { get; set; }
        public string DatasetType { get; set; }
    }
}
