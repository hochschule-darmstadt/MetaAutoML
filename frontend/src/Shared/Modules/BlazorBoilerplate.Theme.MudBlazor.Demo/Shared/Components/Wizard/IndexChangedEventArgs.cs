using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BlazorBoilerplate.Theme.Material.Demo.Shared.Components.Wizard
{
    /// <summary>
    /// This class contains arguments for the IndexChanged event.
    /// </summary>
    public class IndexChangedEventArgs
    {
        // *******************************************************************
        // Properties.
        // *******************************************************************

        #region Properties

        /// <summary>
        /// This property indicates the new index.
        /// </summary>
        public int? NewIndex { get; set; }

        /// <summary>
        /// This property indicates the current index.
        /// </summary>
        public int? CurrentIndex { get; internal set; }

        #endregion
    }
}