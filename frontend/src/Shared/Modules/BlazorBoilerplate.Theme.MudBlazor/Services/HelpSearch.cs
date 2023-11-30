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
        private List<Server.SearchRelevantData> _ontologyData;

        private List<HelpArticle> _helpSiteData;
        public HelpSearch(IApiClient client, IViewNotifier notifier, IStringLocalizer<Global> L)
        {
            _client = client;
            _notifier = notifier;
            _l = L;
            _ontologyData = new List<Server.SearchRelevantData>();
            _helpSiteData = new List<HelpArticle>();
        }

        /// <summary>
        /// Indicate if the search cache has loaded yet
        /// </summary>
        /// <value></value>
        public bool IsCacheLoaded {
            get
            {
            return _ontologyData.Any() && _helpSiteData.Any();
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
            ApiResponseDto<GetSearchRelevantDataResponseDto> apiResponseDto;

            try
            {
                apiResponseDto = await _client.GetSearchRelevantData();
                _ontologyData = apiResponseDto.Result.SearchData;

                //TODO: load Data from Help Site Json here

                if(OnSearchCacheLoadedCallback != null)
                {
                    OnSearchCacheLoadedCallback();
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
        public List<String> GetAllAutocompleteOptions()
        {
            return _ontologyData
                .SelectMany(e => new[]{ e.Label, e.AltLabels})
                .Concat(_helpSiteData.SelectMany(e => new[]{ e.Title }))
                .Where(label => !string.IsNullOrWhiteSpace(label))
                .Distinct()
                .ToList();
        }

        /// <summary>
        ///
        /// </summary>
        /// <param name="search"></param>
        /// <returns></returns>
        public List<String> GetAutocompleteOptions(string search)
        {
            return GetAllAutocompleteOptions().FindAll(e => e.Contains(search)).ToList();
        }

        //TODO: define generic model for returning ML and Help Page Article Data
    }
}
