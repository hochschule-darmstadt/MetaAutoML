using System;
using Microsoft.AspNetCore.Components;
using System.Net.NetworkInformation;
using GTour.Abstractions;


namespace BlazorBoilerplate.Theme.Material.Services
{
    public class TourService
    {
        private readonly IGTourService _gTourService;
        public TourService(IGTourService gTourService)
        {
            _gTourService = gTourService;
        }
        
        private string GetQueryParam(string paramName, string uri)
        {
            var uriBuilder = new UriBuilder(uri);
            var q = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            return q[paramName] ?? "";
        }


        public async Task checkIfUserTourIsActivated(string uri)
        {
            string queryParam = this.GetQueryParam("TourStep", uri);
            if (!string.IsNullOrEmpty(queryParam))
            {
                await _gTourService.StartTour("FormGuidedTour", queryParam);
            }
        }
    }
}

