using BlazorBoilerplate.Shared.Models;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IHelpSearch
    {
        Task LoadSearchCache();
        List<string> GetAllAutocompleteOptions();
        List<string> GetAutocompleteOptions(string search);

        List<HelpSearchEntry> GetFulltextSearch(string search);
    }
}
