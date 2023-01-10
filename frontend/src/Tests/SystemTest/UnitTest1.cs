
using System.Collections.Generic;
using System.Net.Http.Headers;
using System.Reflection;
using System.IO;
using BlazorBoilerplate.Theme.Material.Services;
using BlazorBoilerplate.Shared.Services;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using IdentityModel.Client;
using System;
using MudBlazor;
using BlazorBoilerplate.Shared.Interfaces;
using Microsoft.Extensions.Localization;
using NSubstitute;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.AspNetCore.Components.Forms;
using static FsKaggle.CredentialsSource;

//using Microsoft.Extensions.DependencyInjection;

namespace SystemTest
{
    [TestClass]
    public class UnitTest1
    {
        private string _dataDir = "";

        [TestInitialize]
        public async Task InitializeTestsAsync()
        {
            string rootDirectory = AppDomain.CurrentDomain.BaseDirectory;
            if (rootDirectory.Contains("frontend"))
            {
                rootDirectory = rootDirectory.Substring(0, rootDirectory.IndexOf("frontend")-1);
                _dataDir = string.Format($"{rootDirectory}\\Data");
                _dataDir = new Uri(_dataDir).AbsolutePath;
            }

            if (!Directory.Exists(_dataDir))
                Directory.CreateDirectory(_dataDir);

            KaggleApiClient apiCLient = new KaggleApiClient();
            await apiCLient.DownloadCompetitionData(_dataDir, "titanic");

        }

        [TestMethod]
        public async Task TestMethod1()
        {
            MockApiClient mockClient = new();
            MockViewNotifier mockNotifier = new();
            var mockIStringLocalizer = Substitute.For<IStringLocalizer<Global>>();
            mockIStringLocalizer["Operation Failed"].Returns(new LocalizedString("Operation Failed", "Operation Failed"));
            
            
            await using FileStream fs = new(String.Format($"{_dataDir}\\titanic"), FileMode.Open);            
            FileUploader uploader = new(mockClient, mockNotifier, mockIStringLocalizer);
            //TODO: somehow set uploader.UploadFileContent to the titanic dataset

            Task testedMethod = uploader.UploadDataset();
            await testedMethod;
            Assert.IsTrue(testedMethod.IsCompletedSuccessfully);        
            
        }

        [TestCleanup]
        public void CleanUpData()
        {
            Directory.Delete(_dataDir, true);
        }
    }
}