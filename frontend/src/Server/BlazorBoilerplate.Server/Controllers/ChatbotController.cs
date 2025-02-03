using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Server.Managers;
using BlazorBoilerplate.Shared.Dto.Chat;
using BlazorBoilerplate.Shared.Dto.Ontology;
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
    public class ChatbotController : Controller
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IChatbotManager _chatbotManager;
        public ChatbotController(IStringLocalizer<Global> l, IChatbotManager chatbotManager)
        {
            L = l;
            _chatbotManager = chatbotManager;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> SendChatMessage(SendChatMessageRequestDto request)
            => ModelState.IsValid ?
                await _chatbotManager.SendChatMessage(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);
    }
}
