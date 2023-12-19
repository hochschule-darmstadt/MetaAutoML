using BlazorBoilerplate.Shared.Models;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IHelpSearch
    {
        Task LoadSearchCache();
        List<HelpSearchEntry> SearchEntries { get; }
        List<HelpSearchEntry> SearchTop10(string search);
        List<HelpSearchEntry> SearchAll(string search);
    }
}
