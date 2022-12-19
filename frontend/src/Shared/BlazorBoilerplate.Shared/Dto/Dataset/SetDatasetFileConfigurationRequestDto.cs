using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class SetDatasetFileConfigurationRequestDto
    {
        public string DatasetId { get; set; }
        public Dictionary<string, dynamic> Configuration { get; set; }
        public Dictionary<string, ColumnsConfiguration> ColumnsConfiugration { get; set; }
    }

    public class ColumnsConfiguration
    {
        public string DataTypeSelected { get; set; }
        public string RoleSelected { get; set; }
    }
}
