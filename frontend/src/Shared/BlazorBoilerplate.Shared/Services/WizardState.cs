using System;
using System.Collections.Generic;
using BlazorBoilerplate.Shared.Dto.AutoML;

namespace BlazorBoilerplate.Shared.Services
{
    public class WizardState{
        public StartAutoMLRequestDto automlRequest;

        public bool IsCompleted()
        {
            switch (automlRequest.DatasetType)
            {
                case ":tabular":
                    var target = automlRequest.Configuration["target"]["target"];
                    if (string.IsNullOrEmpty(automlRequest.Task) | string.IsNullOrEmpty((string)target))
                    {
                        return false;
                    }
                    return true;
                case ":image":
                    return false;
                case ":panel":
                    return false;
            }
            return false;
        }
    }
}