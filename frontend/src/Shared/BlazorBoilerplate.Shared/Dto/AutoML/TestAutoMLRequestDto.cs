using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Dto.AutoML
{
    public class TestAutoMLRequestDto
    {
        public byte[] TestData { get; set; }
        public string ModelId { get; set; }
    }
}