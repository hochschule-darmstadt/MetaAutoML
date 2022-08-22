using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class SetDatasetFileConfigurationRequestDto
    {
        public string DatasetIdentifier { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
    }
}
