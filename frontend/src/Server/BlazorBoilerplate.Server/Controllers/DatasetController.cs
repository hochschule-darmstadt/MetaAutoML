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

        [HttpGet]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDatasetTypes()
            => ModelState.IsValid ?
                await _datasetManager.GetDatasetTypes() :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDataset(GetDatasetRequestDto dataset)
            => ModelState.IsValid ?
                await _datasetManager.GetDataset(dataset) :
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
        public async Task<ApiResponse> GetTabularDatasetColumn(GetTabularDatasetColumnRequestDto dataset)
            => ModelState.IsValid ?
                await _datasetManager.GetTabularDatasetColumn(dataset) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetDatasetPreview(GetDatasetPreviewRequestDto dataset)
            => ModelState.IsValid ?
                await _datasetManager.GetDatasetPreview(dataset) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> Upload(FileUploadRequestDto file)
            => ModelState.IsValid ?
                await _datasetManager.Upload(file) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        //[HttpPost]
        //[ProducesResponseType(Status200OK)]
        //[ProducesResponseType(Status400BadRequest)]
        //[ProducesResponseType(Status404NotFound)]
        //public async Task<ApiResponse> UploadData(IFormFile files)
        //    => ModelState.IsValid ?
        //        await _datasetManager.UploadData(files) :
        //        new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> SetDatasetConfiguration(SetDatasetFileConfigurationRequestDto dataset)
            => ModelState.IsValid ?
                await _datasetManager.SetDatasetConfiguration(dataset) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);
    }
}
