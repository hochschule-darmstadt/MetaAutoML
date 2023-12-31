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
        /// <summary>
        /// Get the value of a query parameter of a uri
        /// </summary>
        /// <param name="paramName"></param> name of the query parameter
        /// <param name="uri"></param> uri in which a query parameter is used
        /// <returns></returns> returns the value of a query parameter
        private string GetQueryParam(string paramName, string uri)
        {
            var uriBuilder = new UriBuilder(uri);
            var q = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
            return q[paramName] ?? "";
        }
        /// <summary>
        /// Checks if a tour is activated at the moment
        /// When a tour is activated the query parameter "TourStep" is part of the uri
        /// </summary>
        /// <param name="uri"></param>current uri 
        /// <returns></returns>returns true in case the tour is activated
        public bool checkIfUserTourIsActivated(string uri)
        {
            string queryParam = this.GetQueryParam("TourStep", uri);
            if (!string.IsNullOrEmpty(queryParam))
            {
                return true;
            }
            else { return false; }
        }

        /// <summary>
        /// Checks if a tour is activated
        /// When a tour is activated the query parameter "TourStep" is part of the uri
        /// when you navigate to a new page you have to start the tour there if the tour is activated at the moment
        /// </summary>
        /// <param name="uri"></param>current uri 
        public async Task checkIfUserTourIsActivatedAndStartTour(string uri)
        {
            string queryParam = this.GetQueryParam("TourStep", uri);
            if (!string.IsNullOrEmpty(queryParam))
            {
                await _gTourService.StartTour("FormGuidedTour", queryParam);
            }
        }
        /// <summary>
        /// when a step of the tour is on a new page, the step has to be included to the uri
        ///
        /// </summary>
        /// <param name="step"></param>next tour step
        /// <param name="uri"></param>uri of the new step 
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

