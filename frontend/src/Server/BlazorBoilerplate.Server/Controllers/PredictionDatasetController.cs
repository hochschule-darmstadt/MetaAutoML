using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.PredictionDataset;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Localization;
using Microsoft.Extensions.Logging;
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
    public class PredictionDatasetController : ControllerBase
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IPredictionDatasetManager _predictionDatasetManager;
        private readonly ILogger<DatasetController> _logger;
        public PredictionDatasetController(IStringLocalizer<Global> l, IPredictionDatasetManager predictionDatasetManager, ILogger<DatasetController> logger)
        {
            L = l;
            _predictionDatasetManager = predictionDatasetManager;
            _logger = logger;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> UploadPredictionDataset(UploadPredictionDatasetRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.UploadPredictionDataset(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetPredictionDatasets(GetPredictionDatasetsRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.GetPredictionDatasets(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetPredictionDataset(GetPredictionDatasetRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.GetPredictionDataset(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> DeletePredictionDataset(DeletePredictionDatasetRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.DeletePredictionDataset(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);
    }
}
