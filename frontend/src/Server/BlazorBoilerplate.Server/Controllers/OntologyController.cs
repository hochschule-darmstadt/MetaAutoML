using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Server.Managers;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Localization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using static Microsoft.AspNetCore.Http.StatusCodes;

namespace BlazorBoilerplate.Server.Controllers
{
    [ApiResponseException]
    [Route("api/[controller]/[action]")]
    [Authorize]
    [ApiController]
    public class OntologyController : Controller
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IOntologyManager _ontologyManager;
        public OntologyController(IStringLocalizer<Global> l, IOntologyManager ontologyManager)
        {
            L = l;
            _ontologyManager = ontologyManager;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]   
        public async Task<ApiResponse> GetAutoMlSolutionsForConfiguration(GetAutoMlSolutionsForConfigurationRequestDto request)
            => ModelState.IsValid ?
                await _ontologyManager.GetAutoMlSolutionsForConfiguration(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetMlLibrariesForTask(GetMlLibrariesForTaskRequestDto task)
            => ModelState.IsValid ?
            await _ontologyManager.GetMlLibrariesForTask(task) :
            new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetTasksForDatasetType(GetTasksForDatasetTypeRequestDto dataset)
            => ModelState.IsValid ?
            await _ontologyManager.GetTasksForDatasetType(dataset) :
            new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]   
        public async Task<ApiResponse> GetAvailableStrategies(GetAvailableStrategiesRequestDto request)
            => ModelState.IsValid ?
                await _ontologyManager.GetAvailableStrategies(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpGet]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDatasetTypes()
        => ModelState.IsValid ?
                await _ontologyManager.GetDatasetTypes() :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpGet]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public Task<ApiResponse> GetAutoMlParameters(GetAutoMlParametersRequestDto request) =>
            ModelState.IsValid ?
                _ontologyManager.GetAutoMlParameters(request) :
                Task.FromResult(new ApiResponse(Status400BadRequest, L["InvalidData"]));
    }
}
