using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Prediction;
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
    public class PredictionController : ControllerBase
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IPredictionManager _predictionDatasetManager;
        private readonly ILogger<DatasetController> _logger;
        public PredictionController(IStringLocalizer<Global> l, IPredictionManager predictionDatasetManager, ILogger<DatasetController> logger)
        {
            L = l;
            _predictionDatasetManager = predictionDatasetManager;
            _logger = logger;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> UploadPrediction(UploadPredictionRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.UploadPrediction(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetPrediction(GetPredictionRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.GetPrediction(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);


        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetPredictions(GetPredictionsRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.GetPredictions(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> DownloadPrediction(DownloadPredictionRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.DownloadPrediction(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> DeletePrediction(DeletePredictionRequestDto request)
            => ModelState.IsValid ?
                await _predictionDatasetManager.DeletePrediction(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);
    }
}
