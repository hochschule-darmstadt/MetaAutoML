using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Interfaces;
using BlazorBoilerplate.Shared.Localizer;
using BlazorBoilerplate.Shared.Services;
using Microsoft.Extensions.Localization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class DatasetPreviewWorker : IDatasetPreviewWorker
    {
        private IApiClient _client;
        private IViewNotifier _notifier;
        private IStringLocalizer<Global> L;
        public DatasetPreviewWorker(IApiClient client, IViewNotifier notifier, IStringLocalizer<Global> l)
        {
            _client = client;
            _notifier = notifier;
            L = l;
        }
        public async Task UpdateDatasetFileConfiguration(GetDatasetResponseDto dataset)
        {
            try
            {
                SetDatasetFileConfigurationRequestDto request = new SetDatasetFileConfigurationRequestDto()
                {
                    Configuration = dataset.Dataset.Configuration,
                    DatasetIdentifier = dataset.Dataset.Identifier
                };
                ApiResponseDto apiResponse = await _client.SetDatasetFileConfiguration(request);

                if (apiResponse.IsSuccessStatusCode)
                {
                    _notifier.Show("Dataset analysis completed for: " + dataset.Dataset.Name, ViewNotifierType.Success, L["Operation Successful"]);
                }
                else
                {
                    _notifier.Show(apiResponse.Message + " : " + apiResponse.StatusCode, ViewNotifierType.Error, L["Operation Failed"]);
                }
            }
            catch (Exception ex)
            {
                _notifier.Show(ex.GetBaseException().Message, ViewNotifierType.Error, L["Operation Failed"]);
            }
        }
    }
}
