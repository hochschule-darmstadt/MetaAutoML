using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.General;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{
    public class GeneralInformationManager : IGeneralInformation
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
            GetHomeOverviewInformationResponseDto response = new GetHomeOverviewInformationResponseDto();
            GetHomeOverviewInformationRequest infoRequest = new GetHomeOverviewInformationRequest();
            var username = _httpContextAccessor.HttpContext.User.FindFirst("omaml").Value;
            try
            {
                infoRequest.User = username;
                var reply = _client.GetHomeOverviewInformation(infoRequest);
                response.TotalDatasetAmount = reply.DatasetAmount;
                response.TotalModelAmount = reply.ModelAmount;
                response.TotalTrainingAmount = reply.TrainingAmount;
                response.RunningTrainingAmount = reply.RunningTrainingAmount;
                return new ApiResponse(Status200OK, null, response);

            }
            catch (Exception ex)
            {

                return new ApiResponse(Status404NotFound, ex.Message);
            }
        }
    }
}
