using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BlazorBoilerplate.Shared.Dto.Ontology;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface ICacheManager
    {
        Task<ObjectInfomationDto> GetObjectInformation(string id);
        Task<List<ObjectInfomationDto>> GetObjectInformationList(List<string> ids);
    }
}
