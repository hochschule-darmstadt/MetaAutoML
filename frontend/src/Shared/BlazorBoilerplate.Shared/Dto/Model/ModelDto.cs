using BlazorBoilerplate.Server;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using BlazorBoilerplate.Shared.Dto.Ontology;

namespace BlazorBoilerplate.Shared.Dto.Model
{

    public class ModelDto
    {
        public string Identifier { get; set; }
        public string TrainingIdentifier { get; set; }
        public double TestScore { get; set; }
        public int Runtime { get; set; }
        public ObjectInfomationDto MlModelType { get; set; }
        public ObjectInfomationDto MlLibrary { get; set; }
        public string Status { get; set; }
        public List<string> Messages { get; set; }
        public double PredictionTime { get; set; }
        public ObjectInfomationDto AutoMl { get; set; }
        public string DatasetIdentifier { get; set; }
        public Dictionary<string, dynamic> Explanation { get; set; }

        public ModelDto(Server.Model model, ObjectInfomationDto mlModelType, ObjectInfomationDto mlLibrary, ObjectInfomationDto autoMl)
        {
            Identifier = model.Identifier;
            TrainingIdentifier = model.TrainingIdentifier;
            TestScore = model.TestScore;
            Runtime = model.Runtime;
            MlModelType = mlModelType;
            MlLibrary = mlLibrary;
            Status = model.Status;
            Messages = model.StatusMessages.ToList();
            PredictionTime = model.PredictionTime;
            AutoMl = autoMl;
            DatasetIdentifier = model.DatasetIdentifier;
            Explanation = JsonConvert.DeserializeObject<Dictionary<string, dynamic>>(model.Explanation);
        }
    }
}