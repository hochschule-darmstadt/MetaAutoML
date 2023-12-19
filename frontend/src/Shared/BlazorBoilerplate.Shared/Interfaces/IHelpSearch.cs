using BlazorBoilerplate.Shared.Models;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IHelpSearch
    {
        bool IsCacheLoaded { get; }
        Task LoadSearchCache();
        IEnumerable<HelpSearchEntry> SearchEntries { get; }
        IEnumerable<HelpSearchEntry> SearchTop10(string search);
        IEnumerable<HelpSearchEntry> SearchAll(string search);
    }
}
