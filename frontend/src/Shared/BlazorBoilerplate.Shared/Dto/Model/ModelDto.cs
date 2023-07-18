using BlazorBoilerplate.Server;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Dto.Prediction;
using Newtonsoft.Json.Linq;

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
        public List<string> StatusMessages { get; set; }
        public Dictionary<string, dynamic> Explanation { get; set; }
        public double Emissions { get; set; }
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
            StatusMessages = model.StatusMessages.ToList();
            Explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(model.Explanation);
            Emissions = model.Emission;
        }
        public string GetMlLibraryString()
        {
            string libraries = "";
            foreach (var lib in MlLibrary)
            {
                libraries += lib.Properties["skos:prefLabel"] + ", ";
            }
            //When no library was set yet return the empty string, else remove the alst comma
            if (libraries.Length == 0)
            {
                return libraries;
            }
            return libraries.Remove(libraries.Length - 1);
        }
        public string GetMlModelString()
        {
            string models = "";
            foreach (var model in MlModelType)
            {
                models += model.Properties["skos:prefLabel"] + ", ";
            }
            //When no ml model type was set yet return the empty string, else remove the alst comma
            if (models.Length == 0)
            {
                return models;
            }
            return models.Remove(models.Length - 1);
        }
    }
}
