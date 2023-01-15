using BlazorBoilerplate.Shared.Dto.Dataset;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IDatasetPreviewWorker
    {
        Task UpdateDatasetFileConfiguration(GetDatasetResponseDto dataset);
        Task UpdateDatasetColumnSchemaConfiguration(SetDatasetColumnSchemaConfigurationRequestDto request);
    }
}
