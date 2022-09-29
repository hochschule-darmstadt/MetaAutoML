using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.Model
{
    public class ModelPredictRequestDto
    {
        public byte[] TestData { get; set; }
        public string ModelId { get; set; }
    }
}