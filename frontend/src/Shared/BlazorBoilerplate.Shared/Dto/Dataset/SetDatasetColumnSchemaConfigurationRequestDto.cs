using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Dataset
{
    public class SetDatasetColumnSchemaConfigurationRequestDto
    {
        public string DatasetId { get; set; }
        public string Column { get; set; }
        public string SelectedRole { get; set; } = "";
        public string SelectedDatatype { get; set; } = "";
    }
}
