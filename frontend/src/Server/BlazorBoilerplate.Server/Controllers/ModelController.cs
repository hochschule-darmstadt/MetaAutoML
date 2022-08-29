﻿using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Shared.Dto.AutoML;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Model;
using BlazorBoilerplate.Shared.Localizer;
using BlazorBoilerplate.Theme.Material.Demo.Pages;
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
    public class ModelController : Controller
    {
        private readonly IStringLocalizer<Global> L;
        private readonly IModelManager _modelManager;
        public ModelController(IStringLocalizer<Global> l, IModelManager modelManager)
        {
            L = l;
            _modelManager = modelManager;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> DeleteModel(DeleteModelRequestDto request)
        => ModelState.IsValid ?
                await _modelManager.DeleteModel(request) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetModels(GetModelsRequestDto models)
            => ModelState.IsValid ?
                await _modelManager.GetModels(models) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetModel(GetModelRequestDto model)
            => ModelState.IsValid ?
                await _modelManager.GetModel(model) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetModelExplanation(GetModelExplanationRequestDto model)
            => ModelState.IsValid ?
                await _modelManager.GetModelExplanation(model) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetModelDownload(GetAutoMlModelRequestDto model)
            => ModelState.IsValid ?
                await _modelManager.GetModelDownload(model) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);
    }
}
