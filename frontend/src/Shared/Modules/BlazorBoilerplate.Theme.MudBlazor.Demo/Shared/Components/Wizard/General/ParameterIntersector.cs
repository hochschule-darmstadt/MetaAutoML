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

    public IEnumerable<(string iri, TaskConfiguration.ParameterObject instance)> GetIntersectedParameters(IEnumerable<string> selectedAutoMlSolutionIris)
    {
        var broaderParams = GetBroaderIrisSupportedByAllSolutions(selectedAutoMlSolutionIris);
        foreach (var broaderIri in broaderParams)
        {
            var intersectedValueIris = Parameters
                .Where(p => p.BroaderIri == broaderIri)
                .GroupBy(p => p.ParamIri)
                .Select(g => g.Select(p => p.ValueIri))
                .IntersectAll();

            var firstParamWithBroader = Parameters.First(p => p.BroaderIri == broaderIri);
            yield return (broaderIri, new TaskConfiguration.ParameterObject
            {
                ParameterIri = broaderIri,
                ParameterLabel = firstParamWithBroader.BroaderLabel,
                ParameterType = firstParamWithBroader.ParamType,
                ParameterValues = intersectedValueIris
                    .Select(v => Parameters.First(p => p.ValueIri == v))
                    .Select(p => new TaskConfiguration.ParameterValueViewModel
                    {
                        ValueIri = p.ValueIri,
                        ValueLabel = p.ValueLabel
                    })
                    .ToList()
            });
        }
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
