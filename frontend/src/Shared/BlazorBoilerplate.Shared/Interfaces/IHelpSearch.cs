using System.Threading.Tasks;

namespace BlazorBoilerplate.Shared.Interfaces
{
    public interface IHelpSearch
    {
        Task LoadSearchCache();
        List<String> GetAllAutocompleteOptions();
        List<String> GetAutocompleteOptions(string search);
    }
}
