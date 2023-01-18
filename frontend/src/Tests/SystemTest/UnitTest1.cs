
namespace SystemTest
{
    [TestClass]
    public class UnitTest1
    {
        private string _dataDir = "";

        /// <summary>
        /// Inialization of test enviroment by downloading test datasets.
        /// </summary>
        /// <returns>asynchrous task</returns>
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
        public void TestMethod1()
        {
              
            
        }

        [TestCleanup]
        public void CleanUpData()
        {
            Directory.Delete(_dataDir, true);
        }
    }
}
