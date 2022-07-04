using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Shared.Dto.Ontology;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Server.Managers
{
    public class CacheManager : ICacheManager
    {
        private readonly ILogger<EmailManager> _logger;
        private readonly ControllerService.ControllerServiceClient _client;
        private readonly IDistributedCache _distributedCache;
        public CacheManager(ILogger<EmailManager> logger, ControllerService.ControllerServiceClient client, IDistributedCache distributedCache)
        {
            _logger = logger;
            _client = client;
            _distributedCache = distributedCache;
        }

        /// <summary>
        /// Retrive informations for an rdf key
        /// </summary>
        /// <param name="ids">one rds key (ID)</param>
        /// <returns>object information</returns>
        public async Task<ObjectInfomationDto> GetObjectInformation(string id)
        {
            var result = await GetObjectInformationList(new List<string>() { id });
            return result[0];
        }
        /// <summary>
        /// Retrive informations for a list of rdf keys
        /// </summary>
        /// <param name="ids">list of rds keys (ID)</param>
        /// <returns>list of object information</returns>
        public async Task<List<ObjectInfomationDto>> GetObjectInformationList(List<string> ids)
        {
            List<ObjectInfomationDto> result = new List<ObjectInfomationDto>();
            GetObjectsInformationRequest request = new GetObjectsInformationRequest();
            try
            {
                foreach (var key in ids)
                {
                    var value = _distributedCache.Get(key);
                    //Check if RDF key already exists
                    if (value != null)
                    {
                        ObjectInformation retrievedRdfObject = JsonConvert.DeserializeObject<ObjectInformation>(Encoding.UTF8.GetString(value));
                        //Copy cached label
                        result.Add(new ObjectInfomationDto()
                        {
                            ID = value.ToString(),
                            Properties = new Dictionary<string, string>(retrievedRdfObject.Informations)
                        });
                    }
                    else
                    {
                        //add id to poll list
                        request.Ids.Add(key);
                    }
                }
                //we have already every rdf object in cache, no need to query ontology and controller
                if (result.Count == ids.Count)
                {
                    return result;
                }
                GetObjectsInformationResponse response = _client.GetObjectsInformation(request);
                foreach (var objectInformation in response.ObjectInformations)
                {
                    //copy received RDF object into reply and persist into redis
                    result.Add(new ObjectInfomationDto()
                    {
                        ID = objectInformation.Id,
                        Properties = new Dictionary<string, string>(objectInformation.Informations)
                    });
                    var rdfObject = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(objectInformation));
                    //Delete keys after 22 hours if not used but also after 24 hours of creation to react to Ontology changes
                    var options = new DistributedCacheEntryOptions()
                        .SetAbsoluteExpiration(DateTime.Now.AddHours(24))
                        .SetSlidingExpiration(TimeSpan.FromHours(22));
                    await _distributedCache.SetAsync(objectInformation.Id, rdfObject, options);
                }
            }
            catch (Exception ex)
            {
                //In case redis is not available we always query data from the ontology
                //FALLBACK 
                request.Ids.Add(ids);
                GetObjectsInformationResponse response = _client.GetObjectsInformation(request);
                foreach (var objectInformation in response.ObjectInformations)
                {
                    //copy received RDF object into reply and persist into redis
                    result.Add(new ObjectInfomationDto()
                    {
                        ID = objectInformation.Id,
                        Properties = new Dictionary<string, string>(objectInformation.Informations)
                    });
                }
            }
            return result;
        }
    }
}
