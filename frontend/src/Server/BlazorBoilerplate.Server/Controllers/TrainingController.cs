﻿using BlazorBoilerplate.Infrastructure.Server;
using BlazorBoilerplate.Infrastructure.Server.Models;
using BlazorBoilerplate.Server.Aop;
using BlazorBoilerplate.Server.Managers;
using BlazorBoilerplate.Shared.Dto.Dataset;
using BlazorBoilerplate.Shared.Dto.Training;
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
    public class TrainingController : Controller
    {
        private readonly IStringLocalizer<Global> L;
        private readonly ITrainingManager _trainingManager;
        public TrainingController(IStringLocalizer<Global> l, ITrainingManager trainingManager)
        {
            L = l;
            _trainingManager = trainingManager;
        }

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> DeleteDataset(DeleteTrainingRequestDto training)
            => ModelState.IsValid ?
                await _trainingManager.DeleteTraining(training) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);
        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetTraining(GetTrainingRequestDto training)
            => ModelState.IsValid ?
                await _trainingManager.GetTraining(training) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetTrainingIds(GetTrainingIdsRequestDto training)
            => ModelState.IsValid ?
                await _trainingManager.GetTrainingIds(training) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);

        [HttpPost]
        [ProducesResponseType(Status200OK)]
        [ProducesResponseType(Status400BadRequest)]
        [ProducesResponseType(Status404NotFound)]
        public async Task<ApiResponse> GetAllTrainings(GetAllTrainingsRequestDto training)
            => ModelState.IsValid ?
                await _trainingManager.GetAllTrainings(training) :
                new ApiResponse(Status400BadRequest, L["InvalidData"]);


    }
}
