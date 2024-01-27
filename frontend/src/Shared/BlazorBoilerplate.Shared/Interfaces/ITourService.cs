using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface ITourService
    {
        //public bool checkIfUserTourIsActivated(string uri);
        public bool checkIfUserTourIsActivated();
        Task checkIfUserTourIsActivatedAndStartTour(string uri);
        void navigateToNextPage(string step, string uri);
    }
}
