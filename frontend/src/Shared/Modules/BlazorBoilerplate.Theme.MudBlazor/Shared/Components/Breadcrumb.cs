using Microsoft.AspNetCore.Components;

namespace BlazorBoilerplate.Theme.Material.Shared.Components
{
    public partial class Breadcrumb : ComponentBase, IDisposable
    {
        [CascadingParameter]
        protected internal Breadcrumbs Parent { get; set; }

        [Parameter]
        public string Link { get; set; }

        [Parameter]
        public string Title { get; set; }

        [Parameter]
        public string Icon { get; set; }

        protected override void OnInitialized()
        {
            Parent.Items.Add(this);
        }

        public void Dispose()
        {
            Parent.Items.Remove(this);
        }

        public static Breadcrumb New(string link, string title, string icon) => new Breadcrumb { Link = link, Title = title, Icon = icon };
    }
}
