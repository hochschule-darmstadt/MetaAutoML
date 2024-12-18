using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Shared.Dto.Chat;
using BlazorBoilerplate.Shared.Dto.Ontology;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Infrastructure.Server
{
    public interface IChatbotManager
    {

        Task<ApiResponse> SendChatMessage(SendChatMessageRequestDto request);

    }
}
