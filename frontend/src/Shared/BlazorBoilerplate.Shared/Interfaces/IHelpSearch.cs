using BlazorBoilerplate.Shared.Models;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IHelpSearch
    {
        Task LoadSearchCache();
        List<HelpSearchOption> GetAllAutocompleteOptions();
        List<HelpSearchOption> GetAutocompleteOptions(string search);

        List<HelpSearchEntry> GetFulltextSearch(string search);
    }
}
