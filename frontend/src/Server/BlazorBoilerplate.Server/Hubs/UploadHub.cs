using BlazorBoilerplate.Infrastructure.Storage.DataModels;
using BlazorBoilerplate.Storage;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.SignalR;
using System.Security.Claims;

namespace BlazorBoilerplate.Server.Hubs
{
    public class UploadHub : Hub
    {
        private const string AuthSchemes =
            "Identity.Application" + "," + JwtBearerDefaults.AuthenticationScheme; //Cookie + Token authentication

        public static Dictionary<string, string> userLookup = new();

        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly UserManager<ApplicationUser> _userManager;
        public readonly ILogger<UploadHub> _logger;

        public UploadHub(IHttpContextAccessor httpContextAccessor,
            UserManager<ApplicationUser> userManager,
            ILogger<UploadHub> logger)
        {
            _userManager = userManager;
            _logger = logger;
            _httpContextAccessor = httpContextAccessor;
        }
    }
}
