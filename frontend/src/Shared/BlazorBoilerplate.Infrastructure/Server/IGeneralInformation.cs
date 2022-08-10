using BlazorBoilerplate.Infrastructure.Server.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BlazorBoilerplate.Shared.Dto.General;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IGeneralInformation
    {
        Task<ApiResponse> GetHomeOverviewInformations();
    }
}
