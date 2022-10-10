using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.User;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    public class GeneralInformationManager : IUserInformation
    {
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IHttpContextAccessor _httpContextAccessor;
        public GeneralInformationManager(ControllerService.ControllerServiceClient client, IHttpContextAccessor httpContextAccessor)
        {
            _client = client;
            _httpContextAccessor = httpContextAccessor;
        }
        public async Task<ApiResponse> GetHomeOverviewInformations()
        {
            GetHomeOverviewInformationResponseDto response;
            GetHomeOverviewInformationRequest infoRequest = new GetHomeOverviewInformationRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                infoRequest.UserId = username;
                var reply = _client.GetHomeOverviewInformation(infoRequest);
                response = new GetHomeOverviewInformationResponseDto(reply);
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
