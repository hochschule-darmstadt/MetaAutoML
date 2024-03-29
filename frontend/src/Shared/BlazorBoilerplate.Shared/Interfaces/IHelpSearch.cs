using BlazorBoilerplate.Shared.Models;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IHelpSearch
    {
        bool IsCacheLoaded { get; }
        Task LoadSearchCache();
        void InitWithCachedData(List<HelpSearchEntry> data);
        IEnumerable<HelpSearchEntry> SearchEntries { get; }
        IEnumerable<HelpSearchEntry> SearchTop10(string search);
        IEnumerable<HelpSearchEntry> SearchAll(string search);
    }
}
