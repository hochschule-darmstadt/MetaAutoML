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
                    if (automlRequest.Configuration.ContainsKey("target"))
                    {
                        var target = automlRequest.Configuration["target"]["target"];
                        if (string.IsNullOrEmpty(automlRequest.Task) | string.IsNullOrEmpty((string)target))
                        {
                            return false;
                        }
                        return true;
                    }
                    return false;
                case ":image":
                    //ATM no required parameter
                    return true;
                case ":longitudinal":
                    if (automlRequest.Configuration.ContainsKey("target"))
                    {
                        var target = automlRequest.Configuration["target"]["target"];
                        if (string.IsNullOrEmpty(automlRequest.Task) | string.IsNullOrEmpty((string)target))
                        {
                            return false;
                        }
                        return true;
                    }
                    return false;
            }
            return false;
        }
    }
}