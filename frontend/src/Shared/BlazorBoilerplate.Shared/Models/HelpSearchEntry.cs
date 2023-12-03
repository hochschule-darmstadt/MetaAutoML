using BlazorBoilerplate.Shared.Dto;

namespace BlazorBoilerplate.Shared.Models
{
    public class HelpSearchEntry
    {
        public HelpSearchEntry(Section data)
        {
            Type = HelpSearchResultType.HELP_ARTICLE;
            HelpArticleData = data;
        }

        public HelpSearchEntry(Server.SearchRelevantData data)
        {
            Type = HelpSearchResultType.ONTOLOGY;
            OntologyData = data;
        }

        public HelpSearchResultType Type { get; }
        public Section HelpArticleData { get; }
        public Server.SearchRelevantData OntologyData { get; }

        public string[] AutocompleteTexts {
            get {
                switch(Type)
                {
                    case HelpSearchResultType.ONTOLOGY:
                    {
                        return [OntologyData.Label, OntologyData.AltLabels];
                    }
                    case HelpSearchResultType.HELP_ARTICLE:
                    {
                        return HelpArticleData.Subsections.Select(e => e.SubHeadline)
                            .Concat([HelpArticleData.Headline])
                            .ToArray();
                    }
                    default:
                    {
                        return [];
                    }
                }
            }
        }

        public string[] FullSearchTexts {
            get {
                switch(Type)
                {
                    case HelpSearchResultType.ONTOLOGY:
                    {
                        return [OntologyData.Label, OntologyData.AltLabels, OntologyData.Comment];
                    }
                    case HelpSearchResultType.HELP_ARTICLE:
                    {
                        return HelpArticleData.Subsections.SelectMany(e => new[]{ e.SubHeadline, e.SubText})
                            .Concat([HelpArticleData.Headline, HelpArticleData.Text])
                            .ToArray();
                    }
                    default:
                    {
                        return [];
                    }
                }
            }
        }
    }

    public enum HelpSearchResultType {
        ONTOLOGY,
        HELP_ARTICLE
    }
}
