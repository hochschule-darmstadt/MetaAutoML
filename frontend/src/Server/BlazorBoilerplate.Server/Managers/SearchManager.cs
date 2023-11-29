using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Managers
{

    public class SearchManager: ISearchManager
    {
        private readonly ControllerService.ControllerServiceClient _client;

        public SearchManager(ControllerService.ControllerServiceClient client)
        {
            _client = client;
            UpdateSearchIndex();
        }

        public void UpdateSearchIndex()
        {
            try
            {
                var reply = _client.GetSearchRelevantData(new GetSearchRelevantDataRequest());
                var entries = reply.SearchEntities;
            }
            catch (Exception ex)
            {
                throw ex;
            }
        }

        public async Task<ApiResponse> Search(string name){
            return new ApiResponse(Status200OK, null, "");
        }

    }
}
