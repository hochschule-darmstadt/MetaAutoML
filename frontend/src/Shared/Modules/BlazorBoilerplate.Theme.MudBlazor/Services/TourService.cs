using System;
using Microsoft.AspNetCore.Components;
using System.Net.NetworkInformation;
using GTour.Abstractions;
using MudBlazor;
using BlazorBoilerplate.Theme.Material.Shared.Components;

namespace BlazorBoilerplate.Theme.Material.Services
{
    public class TourService
    {
        private readonly NavigationManager _navigationManager;
        private readonly IGTourService _gTourService;
        public TourService(IGTourService gTourService, NavigationManager navigationManager)
        {
            _gTourService = gTourService;
            _navigationManager = navigationManager;

        }
        
        private string GetQueryParam(string paramName, string uri)
        {
            var uriBuilder = new UriBuilder(uri);
            var q = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            return q[paramName] ?? "";
        }

        public bool checkIfUserTourIsActivated(string uri)
        {
            string queryParam = this.GetQueryParam("TourStep", uri);
            if (!string.IsNullOrEmpty(queryParam))
            {
                return true;
            }
            else { return false; }
        }


        public async Task checkIfUserTourIsActivatedAndStartTour(string uri)
        {
            string queryParam = this.GetQueryParam("TourStep", uri);
            if (!string.IsNullOrEmpty(queryParam))
            {
                await _gTourService.StartTour("FormGuidedTour", queryParam);
            }
        }
        public void navigateToNextPage(string step, string uri)
        {
            // var uri = navigationManager.GetUriWithQueryParameter("TourActivated", true);
            //var shouldUri = navigationManager.ToAbsoluteUri(" ").AbsoluteUri;
            if (uri.EndsWith("/")) { uri = uri.Remove(uri.Length - 1, 1); }
            var uriBuilder = new UriBuilder(uri);
            var q = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            q["TourStep"] = step;
            uriBuilder.Query = q.ToString();
            var newUrl = uriBuilder.ToString();
            _navigationManager.NavigateTo(newUrl);
            //await context.NextStep();
            //await GTourService.StartTour("FormGuidedTour", "forthStep");

        }
    }
}

