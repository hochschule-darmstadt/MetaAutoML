using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class ModelRuntimeProfile
    {
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public ModelRuntimeProfile()
        {

        }
        public ModelRuntimeProfile(Server.ModelruntimeProfile runtime)
        {
            StartTime = runtime.StartTime.ToDateTime();
            EndTime = runtime.EndTime.ToDateTime();
        }
    }
}
