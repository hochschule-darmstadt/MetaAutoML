using Karambolo.Common;

namespace BlazorBoilerplate.Shared.Models
{
    public class HelpSearchOption
    {
        public HelpSearchOption(HelpSearchResultType originType, string text, string subText = "", string entryClass = "")
        {
            OriginType = originType;
            string shownText = "";
            shownText += text;

            if(!subText.IsNullOrEmpty())
            {
                shownText += " (" + subText + ")";
            }

            if(!entryClass.IsNullOrEmpty())
            {
                shownText += " [" + entryClass + "]";
            }

            Text = shownText.Replace(":", "");
        }

        public HelpSearchResultType OriginType { get; }
        public string Text { get; }

        public override string ToString()
        {
            return Text;
        }

        public override bool Equals(object obj)
        {
            //Check for null and compare run-time types.
            if ((obj == null) || ! this.GetType().Equals(obj.GetType()))
            {
                return false;
            }

            HelpSearchOption other = (HelpSearchOption) obj;

            return this.OriginType == other.OriginType && this.Text == other.Text;
        }
    }
}
