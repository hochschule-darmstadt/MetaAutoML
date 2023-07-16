using BlazorBoilerplate.Server;

namespace BlazorBoilerplate.Shared.Dto.Ontology;

public class AutoMlParameterDto
{
    public AutoMlParameterDto(ObjectInfomationDto automl, ObjectInfomationDto parameter, ObjectInfomationDto parameterType, ObjectInfomationDto broader, ObjectInfomationDto value)
    {
        AutoML = automl;
        Parameter = parameter;
        ParameterType = parameterType;
        Broader = broader;
        Value = value;
    }
    public ObjectInfomationDto AutoML { get; set; }
    public ObjectInfomationDto Parameter { get; set; }
    public ObjectInfomationDto ParameterType { get; set; }
    public ObjectInfomationDto Broader { get; set; }
    public ObjectInfomationDto Value { get; set; }


    /// <summary>
    /// Whether the parameter expects a scalar value (e.g. a string or a number)
    /// </summary>
    /// <returns></returns>
    public bool IsScalar =>
        // if value is not set, that means, that this object does not represent an option => It must be a scalar parameter
        string.IsNullOrWhiteSpace(Value.ID);

    /// <summary>
    /// The iri that identifies the most abstract type for this parameter.
    /// </summary>
    /// <returns></returns>
    public string BroadestIri => !string.IsNullOrWhiteSpace(Broader.ID) ? Broader.ID : Parameter.ID;

    /// <summary>
    /// The label for the most abstract type for this parameter.
    /// </summary>
    /// <returns></returns>
    public string BroadestLabel => !string.IsNullOrWhiteSpace(Broader.ID) ? Broader.Properties["skos:prefLabel"] : Parameter.Properties["skos:prefLabel"];
}

public class GetAutoMlParametersResponseDto
{
    public List<AutoMlParameterDto> AutoMlParameters { get; set; }
}
