using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Chat;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Storage;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    /// <summary>
    /// Manages all RPC calls which are connected to requests for knowledge from the Ontology
    /// </summary>
    public class ChatbotManager : IChatbotManager
    {
        private readonly ApplicationDbContext _dbContext;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly ICacheManager _cacheManager;
        public ChatbotManager(ApplicationDbContext dbContext, ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor, ICacheManager cacheManager)
        {
            _dbContext = dbContext;
            _client = client;
            _httpContextAccessor = httpContextAccessor;
            _cacheManager = cacheManager;
        }

        public async Task<ApiResponse> SendChatMessage(SendChatMessageRequestDto request)
        {
            // call grpc method
            SendChatMessageRequest requestGrpc = new SendChatMessageRequest();
            SendChatMessageResponseDto response;
            try
            {
                requestGrpc.ChatMessage = request.ChatMessage;
                requestGrpc.NewChat = request.NewChat;
                var reply = _client.SendChatMessage(requestGrpc);
                response = new SendChatMessageResponseDto(reply.ControllerResponse);
                return new ApiResponse(Status200OK, null, response);
            }
            catch (Exception ex)
            {
                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
