using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.AutoML
{
    public class AutoMLConfiguration : IAutoMLConfiguration
    {
        public AutoML.AutoMLTarget Target { get; set; }
        public Dictionary<string,Server.DataType> Features { get; set; }
        public string GetSummary()
        {
            throw new NotImplementedException();
        }
    }
}
