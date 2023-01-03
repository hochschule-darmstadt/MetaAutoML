using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Shared.Dto.Dataset;
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
    public class DatasetController : ControllerBase
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IDatasetManager _datasetManager;
        private readonly ILogger<DatasetController> _logger;
        public DatasetController(IStringLocalizer<Global> l, IDatasetManager datasetManager, ILogger<DatasetController> logger)
        {
            L = l;
            _datasetManager = datasetManager;
            _logger = logger;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        [ProducesResponseType(Status406NotAcceptable)]
        public async Task<ApiResponse> UploadDataset(UploadDatasetRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.UploadDataset(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpGet]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDatasets()
            => ModelState.IsValid ?
                await _datasetManager.GetDatasets() :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDataset(GetDatasetRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.GetDataset(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDatasetPreview(GetDatasetPreviewRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.GetDatasetPreview(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);


        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.GetTabularDatasetColumn(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> SetDatasetFileConfiguration(SetDatasetFileConfigurationRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.SetDatasetFileConfiguration(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> SetDatasetColumnSchemaConfiguration(SetDatasetColumnSchemaConfigurationRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.SetDatasetColumnSchemaConfiguration(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDatasetAnalysis(GetDatasetAnalysisRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.GetDatasetAnalysis(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> DeleteDataset(DeleteDatasetRequestDto request)
            => ModelState.IsValid ?
                await _datasetManager.DeleteDataset(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        //[HttpPost]
        //[ProducesResponseType(Status200OK)]
        //[ProducesResponseType(Status400BadRequest)]
        //[ProducesResponseType(Status404NotFound)]
        //public async Task<ApiResponse> UploadData(IFormFile files)
        //    => ModelState.IsValid ?
        //        await _datasetManager.UploadData(files) :
        //        new ApiResponse(Status400BadRequest, L["InvalidData"])
    }
}
