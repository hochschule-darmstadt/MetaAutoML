namespace BlazorBoilerplate.Shared.Dto.Ontology;

public class GetAutoMlParametersRequestDto 
{
    public string TaskIri { get; set; }
    public List<string> AutoMls { get; set; }
}