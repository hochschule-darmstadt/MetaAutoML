using Microsoft.AspNetCore.Components;
using MudBlazor;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Theme.Material.Demo.Shared.Components.Wizard
{
    /// <summary>
    /// This class is the code-behind for the <see cref="WizardPanel"/> 
    /// razor component.
    /// </summary>
    public partial class MuddyWizardPanel : MudComponentBase, IAsyncDisposable
    {
        // *******************************************************************
        // Fields.
        // *******************************************************************
        //Credit: https://github.com/CodeGator/CG.Blazor.Wizard/

        #region Fields

        /// <summary>
        /// This field indicate whether the component has been disposed.
        /// </summary>
        private bool _disposed;

        #endregion

        // *******************************************************************
        // Properties.
        // *******************************************************************

        #region Properties

        /// <summary>
        /// This property contains the parent of the component.
        /// </summary>
        [CascadingParameter]
        protected internal MuddyWizard Parent { get; set; }

        /// <summary>
        /// This property contains the child content for the component.
        /// </summary>
        [Parameter]
        public RenderFragment ChildContent { get; set; }

        /// <summary>
        /// This property contains the title for the component.
        /// </summary>
        [Parameter]
        public string Title { get; set; }

        /// <summary>
        /// This property contains the description for the component.
        /// </summary>
        [Parameter]
        public string Description { get; set; }

        #endregion

        // *******************************************************************
        // Protected methods.
        // *******************************************************************

        #region Protected methods

        /// <summary>
        /// This method is called to initialize the component.
        /// </summary>
        protected override void OnInitialized()
        {
            // Add ourselves to the parent wizard.
            Parent.AddPanel(this);

            // Give the base class a chance.
            base.OnInitialized();
        }

        // *******************************************************************

        /// <summary>
        /// This method is called to dispose of the component.
        /// </summary>
        /// <returns>A task to perform the operation.</returns>
        public async ValueTask DisposeAsync()
        {
            // Have we already been disposed?
            if (_disposed == true)
            {
                return; // Nothing to do.
            }

            // Mark that we've been disposed.
            _disposed = true;

            // Cleanup our reference in the parent wizard.
            await Parent?.RemovePanel(this);

            // Prevent derived types from having the implement IDisposable.
            GC.SuppressFinalize(this);
        }

        #endregion
    }
}