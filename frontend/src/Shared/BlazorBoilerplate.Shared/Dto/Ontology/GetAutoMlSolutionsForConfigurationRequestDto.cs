﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Ontology
{
    public class GetAutoMlSolutionsForConfigurationRequestDto
    {
        public Dictionary<string, string> Configuration { get; set; }
    }
}
