using BlazorBoilerplate.Shared.Dto.Ontology;

namespace BlazorBoilerplate.Theme.Material.Demo.Shared.Components.Wizard.General;

/// <summary>
/// Class encapsulating the intersection of the auto ml parameters for the configuration wizard.
/// One instance of the wizard only needs one instance of the intersector,
/// because all functions of this class automatically use the current state.
/// </summary>
public class ParameterIntersector
{
    private readonly Func<IEnumerable<AutoMlParameterDto>> _parameterGetter;

    private IEnumerable<AutoMlParameterDto> Parameters => _parameterGetter();

    /// <summary>
    /// Creates a new instance of this class.
    /// </summary>
    /// <param name="parameterGetter">A function returning the current list of parameters</param>
    public ParameterIntersector(Func<IEnumerable<AutoMlParameterDto>> parameterGetter)
    {
        _parameterGetter = parameterGetter;
    }

    private IEnumerable<string> GetBroaderIrisSupportedByAllSolutions(IEnumerable<string> selectedAutoMlSolutionIris)
    {
        return Parameters
            .GroupBy(p => p.BroaderIri)
            .Where(g => g.Select(p => p.AutoMlIri).Distinct().Count() == selectedAutoMlSolutionIris.Count())
            .Select(g => g.Key);
    }

    public IEnumerable<TaskConfiguration.ParameterObject> GetIntersectedParameters(IEnumerable<string> selectedAutoMlSolutionIris)
    {
        var broaderParams = GetBroaderIrisSupportedByAllSolutions(selectedAutoMlSolutionIris);
        foreach (var broaderIri in broaderParams)
        {
            var parametersForBroader = Parameters
                .Where(p => p.BroaderIri == broaderIri)
                .ToList();

            if (!AreTypesCompatible(parametersForBroader))
            {
                // The types mismatch. Therefore an intersection is not possible
                continue;
            }

            List<string> intersectedValueIris = null;
            if (IsParameterListType(parametersForBroader.First().ParamType))
            {
                intersectedValueIris = GetIntersectedValues(parametersForBroader);

                if (!intersectedValueIris.Any())
                {
                    // There are no selectable values => intersected parameter cannot be filled.
                    continue;
                }
            }
            var parameterType = GetMostRestrictiveTypeIri(parametersForBroader);

            yield return new TaskConfiguration.ParameterObject
            {
                ParameterIri = broaderIri,
                ParameterLabel = parametersForBroader.First().BroaderLabel,
                ParameterType = parameterType,
                ParameterValues = intersectedValueIris?.Select(ValueIriToValueViewModel).ToList()
            };
        }
    }

    private bool IsParameterListType(string typeIri)
    {
        return typeIri == ":single_value" || typeIri == ":list";
    }

    private List<string> GetIntersectedValues(IEnumerable<AutoMlParameterDto> parameters)
    {
        return parameters
            .GroupBy(p => p.ParamIri)
            .Select(g => g.Select(p => p.ValueIri))
            .IntersectAll()
            .ToList();
    }

    private bool AreTypesCompatible(IEnumerable<AutoMlParameterDto> parameters)
    {
        string getMostRestrictiveSupportedParameterType(string paramType) =>
            paramType switch
            {
                ":list" => ":single_value",
                _ => paramType
            };

        return parameters.DistinctBy(p => getMostRestrictiveSupportedParameterType(p.ParamType)).Count() == 1;
    }

    private string GetMostRestrictiveTypeIri(IEnumerable<AutoMlParameterDto> parameters)
    {
        return parameters.Select(p => p.ParamType).Min(new ParamTypeComparer());
    }

    private TaskConfiguration.ParameterValueViewModel ValueIriToValueViewModel(string iri)
    {
        var parameterWithValue = Parameters.First(p => p.ValueIri == iri);
        return new TaskConfiguration.ParameterValueViewModel
        {
            ValueIri = iri,
            ValueLabel = parameterWithValue.ValueLabel
        };
    }

}

/// <summary>
/// Comparer that orders parameter types by their restrictiveness.
/// :single_value < :list
/// </summary>
public class ParamTypeComparer : IComparer<string>
{
    public int Compare(string x, string y)
    {
        if (x == y)
        {
            return 0;
        }
        // single value is always the most restrictive
        return x == ":single_value" ? -1 : +1;
    }
}

/// <summary>
/// Class containing extension methods that can be used on Enumerables.
/// </summary>
public static class EnumerableExtensions
{
    /// <summary>
    /// Intersects an enumerable of enumerables.
    /// </summary>
    /// <param name="enumerables">enumerable of enumerables</param>
    /// <typeparam name="T">The type of elements in the enumerables</typeparam>
    /// <returns>An enumerable containing only elements that exist in all enumerables</returns>
    public static IEnumerable<T> IntersectAll<T>(this IEnumerable<IEnumerable<T>> enumerables)
    {
        return enumerables
            .Skip(1)
            .Aggregate(
                new HashSet<T>(enumerables.First()),
                (h, e) => { h.IntersectWith(e); return h; }
            );
    }
}
