using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Shared.Dto.User;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Localization;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Controllers
{
    [ApiResponseException]
    [Route("api/[controller]/[action]")]
    [Authorize]
    [ApiController]
    public class UserController : Controller
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IUserInformation _userManager;
        public UserController(IStringLocalizer<Global> l, IUserInformation userManager)
        {
            L = l;
            _userManager = userManager;
        }

        [HttpGet]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetHomeOverviewInformations()
            => ModelState.IsValid ?
                await _userManager.GetHomeOverviewInformations() :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

    }
}
