using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.Prediction;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class Metric
    {
        public ObjectInfomationDto Name { get; set; }
        public float Score { get; set; }
    }

    public class ModelDto
    {
        public string Id { get; set; }
        public string TrainingId { get; set; }
        public List<PredictionDto> Predictions { get; set; }
        public string Status { get; set; }
        public ObjectInfomationDto AutoMlSolution { get; set; }
        public List<ObjectInfomationDto> MlModelType { get; set; }
        public List<ObjectInfomationDto> MlLibrary { get; set; }
        public List<Metric> Metrics { get; set; }
        public double PredictionTime { get; set; }
        public ModelRuntimeProfile RuntimeProfile { get; set; }
        public string Runtime { get; set; }
        public List<string> StatusMessages { get; set; }
        public double Emissions { get; set; }
        public string DashboardStatus { get; set; }

        public ModelDto()
        {

        }

        public ModelDto(Server.Model model, List<ObjectInfomationDto> mlModelType, List<ObjectInfomationDto> mlLibrary, ObjectInfomationDto autoMl, List<Metric> metrics)
        {
            Id = model.Id;
            TrainingId = model.TrainingId;
            Predictions = new List<PredictionDto>();
            foreach (var item in model.Predictions)
            {
                Predictions.Add(new PredictionDto(item));
            }
            Status = model.Status;
            AutoMlSolution = autoMl;
            MlModelType = mlModelType;
            MlLibrary = mlLibrary;
            Metrics = metrics;
            PredictionTime = model.PredictionTime;
            RuntimeProfile = new ModelRuntimeProfile(model.RuntimeProfile);
            Runtime = RuntimeProfile.ToString();
            StatusMessages = model.StatusMessages.ToList();
            Emissions = model.Emission;
            DashboardStatus = model.DashboardStatus;
        }

        public string GetMlLibraryString()
        {
            string libraries = "";
            List<string> libraryList = new List<string>();
            foreach (var lib in MlLibrary)
            {
                libraryList.Add(lib.Properties["skos:prefLabel"]);
            }
            libraries = string.Join(", ", libraryList).TrimEnd(',');
            return libraries;
        }

        public string GetMlModelString()
        {
            string models = "";
            List<string> modelList = new List<string>();
            foreach (var model in MlModelType)
            {
                modelList.Add(model.Properties["skos:prefLabel"]);
            }
            models = string.Join(", ", modelList).TrimEnd(',');
            return models;
        }
    }
}
