using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Server.Managers
{
    public class CacheManager : ICacheManager
    {
        private readonly ILogger<EmailManager> _logger;
        private readonly ControllerService.ControllerServiceClient _client;
        public CacheManager(ILogger<EmailManager> logger, ControllerService.ControllerServiceClient client)
        {
            //TODO ADD REDIS
            _logger = logger;
            _client = client;
        }

        public Task<ObjectInfomationDto> GetObjectInformation(string id)
        {
            throw new System.NotImplementedException();
        }

        public async Task<List<ObjectInfomationDto>> GetObjectInformationList(List<string> ids)
        {
            List<ObjectInfomationDto> result = new List<ObjectInfomationDto>();
            GetObjectsInformationRequest request = new GetObjectsInformationRequest();
            request.Ids.Add(ids);
            GetObjectsInformationResponse response = _client.GetObjectsInformation(request);
            foreach (var objectInformation in response.ObjectInformations)
            {
                result.Add(new ObjectInfomationDto()
                {
                    ID = objectInformation.Id,
                    Properties = new Dictionary<string, string>(objectInformation.Informations)
                });
            }
            return result;
        }
    }
}
