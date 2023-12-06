using BlazorBoilerplate.Shared.Interfaces;
using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.Extensions.Localization;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Models;


namespace BlazorBoilerplate.Theme.Material.Services
{
    public class HelpSearch : IHelpSearch
    {
        private readonly IApiClient _client;
        private readonly IViewNotifier _notifier;
        private readonly IStringLocalizer<Global> _l;
        private readonly List<HelpSearchEntry> _searchEntries;

        public HelpSearch(IApiClient client, IViewNotifier notifier, IStringLocalizer<Global> L)
        {
            _client = client;
            _notifier = notifier;
            _l = L;
            _searchEntries = new List<HelpSearchEntry>();
        }

        /// <summary>
        /// Indicate if the search cache has loaded yet
        /// </summary>
        /// <value></value>
        public bool IsCacheLoaded {
            get
            {
            return _searchEntries.Any();
            }
        }

        /// <summary>
        /// Callback beeing called if cache data was loaded properly
        /// </summary>
        /// <value></value>
        public Action OnSearchCacheLoadedCallback { get; set; }

        /// <summary>
        /// Load Search Cache Data from Server once for autocompletion to work
        /// </summary>
        /// <returns></returns>
        public async Task LoadSearchCache()
        {
            try
            {
                _searchEntries.Clear();

                ApiResponseDto<GetSearchRelevantDataResponseDto> apiOntologieResponseDto = await _client.GetSearchRelevantData();
                _searchEntries.AddRange(apiOntologieResponseDto.Result.SearchData.Select(e => new HelpSearchEntry(e)));

                List<HelpPageDto> apiHelpPageResponseDto = await _client.GetHelpPageJson();
                _searchEntries.AddRange(apiHelpPageResponseDto.SelectMany(e => e.Sections).Select(e => new HelpSearchEntry(e)));

                if(OnSearchCacheLoadedCallback != null)
                {
                    OnSearchCacheLoadedCallback.Invoke();
                }
            }
            catch (Exception ex)
            {
                _notifier.Show(ex.Message, ViewNotifierType.Error, _l["Operation Failed"]);
            }
        }

        /// <summary>
        /// Get all available auto complete options from search data, may be empty if not loaded yet
        /// </summary>
        /// <returns>List of strings for autocompletion</returns>
        public List<string> GetAllAutocompleteOptions()
        {
            return _searchEntries
                .SelectMany(e => e.AutocompleteTexts)
                .Where(label => !string.IsNullOrWhiteSpace(label))
                .Distinct()
                .ToList();
        }

        /// <summary>
        /// Get all auto complete options filtered by search text
        /// </summary>
        /// <param name="search">text to search options</param>
        /// <returns>List of options matching search</returns>
        public List<string> GetAutocompleteOptions(string search)
        {
            return GetAllAutocompleteOptions().FindAll(e => e.Contains(search)).ToList();
        }

        /// <summary>
        /// Get all full text search result for search term
        /// </summary>
        /// <param name="search">search term</param>
        /// <returns>List of matched search entries</returns>
        public List<HelpSearchEntry> GetFulltextSearch(string search) {
            return _searchEntries
                .Where(entry => entry.FullSearchTexts
                    .Where(text => !string.IsNullOrWhiteSpace(text))
                    .Any(text => text.Contains(search)))
                .ToList();
        }
    }
}
