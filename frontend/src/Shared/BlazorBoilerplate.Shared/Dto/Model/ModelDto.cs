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

    public class ModelDto
    {
        public string Id { get; set; }
        public string TrainingId { get; set; }
        public List<PredictionDto> Predictions { get; set; }
        public string Status { get; set; }
        public ObjectInfomationDto AutoMlSolution { get; set; }
        public ObjectInfomationDto MlModelType { get; set; }
        public ObjectInfomationDto MlLibrary { get; set; }
        public dynamic TestScore { get; set; }
        public double PredictionTime { get; set; }
        public ModelRuntimeProfile RuntimeProfile { get; set; }
        public List<string> StatusMessages { get; set; }
        public Dictionary<string, dynamic> Explanation { get; set; }
        public double Emissions { get; set; }
        public ModelDto()
        {

        }
        public ModelDto(Server.Model model, ObjectInfomationDto mlModelType, ObjectInfomationDto mlLibrary, ObjectInfomationDto autoMl)
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
            TestScore = JObject.Parse(model.TestScore);
            PredictionTime = model.PredictionTime;
            RuntimeProfile = new ModelRuntimeProfile(model.RuntimeProfile);
            StatusMessages = model.StatusMessages.ToList();
            Explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(model.Explanation);
            Emissions = model.Emission;
        }
    }
}
