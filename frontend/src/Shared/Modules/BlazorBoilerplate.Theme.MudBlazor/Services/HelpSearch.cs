using BlazorBoilerplate.Shared.Interfaces;
using BlazorBoilerplate.Shared.Dto;
using BlazorBoilerplate.Shared.Localizer;
using Microsoft.Extensions.Localization;
using BlazorBoilerplate.Shared.Dto.Ontology;
using BlazorBoilerplate.Shared.Models;
using Karambolo.Common;


namespace BlazorBoilerplate.Theme.Material.Services
{
    public class HelpSearch : IHelpSearch
    {
        private readonly IApiClient _client;
        private readonly IViewNotifier _notifier;
        private readonly IStringLocalizer<Global> _l;
        private readonly List<HelpSearchEntry> _ontologieEntries;
        private readonly List<HelpSearchEntry> _helpPageEntries;
        public List<HelpSearchEntry> SearchEntries {
            get
            {
                return _ontologieEntries.Concat(_helpPageEntries).ToList();
            }
        }

        public HelpSearch(IApiClient client, IViewNotifier notifier, IStringLocalizer<Global> L)
        {
            _client = client;
            _notifier = notifier;
            _l = L;
            _ontologieEntries = new List<HelpSearchEntry>();
            _helpPageEntries = new List<HelpSearchEntry>();
        }

        /// <summary>
        /// Indicate if the search cache has loaded yet
        /// </summary>
        /// <value></value>
        public bool IsCacheLoaded {
            get
            {
                return _ontologieEntries.Any() && _helpPageEntries.Any();
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
                _ontologieEntries.Clear();
                _helpPageEntries.Clear();

                ApiResponseDto<GetSearchRelevantDataResponseDto> apiOntologieResponseDto = await _client.GetSearchRelevantData();
                _ontologieEntries.AddRange(apiOntologieResponseDto.Result.SearchData.Select(HelpSearchEntry.ConvertToHelpSearchEntry));

                List<HelpPageDto> apiHelpPageResponseDto = await _client.GetHelpPageJson();
                _helpPageEntries.AddRange(apiHelpPageResponseDto.SelectMany(e => e.Sections)
                    .SelectMany(HelpSearchEntry.ConvertToHelpSearchEntries));

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

        private List<HelpSearchEntry> SearchList(List<HelpSearchEntry> list, string search)
        {
            return list.Select(e => Tuple.Create(e.MatchScore(search), e))
                .Where(e => e.Item1 > 0)
                .OrderByDescending(e => e.Item1)
                .Select(e => e.Item2)
                .Take(10)
                .ToList();
        }

        /// <summary>
        /// search top 10 result for search term
        /// </summary>
        /// <param name="search">search term</param>
        /// <returns>10 matched search entries</returns>
        public List<HelpSearchEntry> SearchTop10(string search) {
            if(search.IsNullOrEmpty())
            {
                return _helpPageEntries.Take(5).Concat(_ontologieEntries.Take(5)).ToList();
            }

            List<HelpSearchEntry> helpEntries = SearchList(_helpPageEntries, search);
            List<HelpSearchEntry> ontologieEntries = SearchList(_ontologieEntries, search);

            // Always return 10 entries from help entries and ontologie
            return helpEntries.Take(5).Concat(ontologieEntries).Take(10).ToList();
        }

        /// <summary>
        /// Get all search results for search term
        /// </summary>
        /// <param name="search">search term</param>
        /// <returns>matched search entries</returns>
        public List<HelpSearchEntry> SearchAll(string search) {
            return SearchList(SearchEntries, search);
        }
    }
}
