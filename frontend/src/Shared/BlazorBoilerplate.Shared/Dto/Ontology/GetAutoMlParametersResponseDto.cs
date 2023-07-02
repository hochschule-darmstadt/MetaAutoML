namespace BlazorBoilerplate.Shared.Dto.Ontology;

public class AutoMlParameterDto
{
    public string AutoMlIri { get; set; }
    public string ParamIri { get; set; }
    public string ParamLabel { get; set; }
    public string ParamType { get; set; }
    public string BroaderIri { get; set; }
    public string BroaderLabel { get; set; }
    public string ValueIri { get; set; }
    public string ValueLabel { get; set; }
    public string SeeAlso { get; set; }
    public string Comment { get; set; }

    /// <summary>
    /// Whether the parameter expects a scalar value (e.g. a string or a number)
    /// </summary>
    /// <returns></returns>
    public bool IsScalar =>
        // if value is not set, that means, that this object does not represent an option => It must be a scalar parameter
        string.IsNullOrWhiteSpace(ValueIri);

    /// <summary>
    /// The iri that identifies the most abstract type for this parameter.
    /// </summary>
    /// <returns></returns>
    public string BroadestIri => !string.IsNullOrWhiteSpace(BroaderIri) ? BroaderIri : ParamIri;

    /// <summary>
    /// The label for the most abstract type for this parameter.
    /// </summary>
    /// <returns></returns>
    public string BroadestLabel => !string.IsNullOrWhiteSpace(BroaderIri) ? BroaderLabel : ParamLabel;
}

public class GetAutoMlParametersResponseDto
{
    public List<AutoMlParameterDto> AutoMlParameters { get; set; }
}
