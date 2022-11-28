namespace BlazorBoilerplate.Shared.Dto.Ontology;

public class AutoMlParameterDto
{
    public string AutoMlIri { get; set; }
    public string ParamIri { get; set; }
    public string ParamLabel { get; set; }
    public string ParamType { get; set; }
    public string ValueIri { get; set; }
    public string ValueLabel { get; set; }
}

public class GetAutoMlParametersResponseDto 
{
    public List<AutoMlParameterDto> AutoMlParameters { get; set; }
}