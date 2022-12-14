using BlazorBoilerplate.Shared.Dto.Ontology;

namespace BlazorBoilerplate.Theme.Material.Demo.Shared.Components.Wizard.General;

public class ParameterIntersector
{
    private readonly Func<IEnumerable<AutoMlParameterDto>> _parameterGetter;

    private IEnumerable<AutoMlParameterDto> Parameters => _parameterGetter();

    public ParameterIntersector(Func<IEnumerable<AutoMlParameterDto>> parameterGetter)
    {
        _parameterGetter = parameterGetter;
    }

    public IEnumerable<string> GetBroaderIrisSupportedByAllSolutions(IEnumerable<string> selectedAutoMlSolutionIris)
    {
        return Parameters
            .GroupBy(p => p.BroaderIri)
            .Where(g => g.Select(p => p.AutoMlIri).Distinct().Count() == selectedAutoMlSolutionIris.Count())
            .Select(g => g.Key);
    }
}

public static class EnumerableExtensions
{
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
