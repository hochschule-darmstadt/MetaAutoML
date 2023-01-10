using BlazorBoilerplate.Shared.Interfaces;
using Microsoft.Extensions.Logging;
using Microsoft.VisualStudio.TestPlatform.TestHost;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SystemTest
{
    internal class MockViewNotifier : IViewNotifier
    {
        public void Show(string message, ViewNotifierType type, string title = null, string icon = null)
        {
           Console.WriteLine(message);
        }
    }
}
