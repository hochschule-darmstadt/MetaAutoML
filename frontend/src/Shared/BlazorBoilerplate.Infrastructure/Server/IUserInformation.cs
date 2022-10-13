using BlazorBoilerplate.Infrastructure.Server.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BlazorBoilerplate.Shared.Dto.User;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IUserInformation
    {
        Task<ApiResponse> GetHomeOverviewInformations();
    }
}
