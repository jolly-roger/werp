/*
* Write your heatmap widget in this file!
*
* The widget should support AT LEAST these options:
*
* @ lowColor  : the color for lowest values
* @ highColor : the color for highest values
* @ dayClass  : the CSS class for day elements
* @ monthClass: the CSS class for month title elements
* @ year      : the year to display
* @ width     : widget width
* @ height    : widget height
* @ cellSize  : the size of a single day element
* @ container : the element to render to
* @ data      : the data to render!
*
* The widget should provide AT LEAST the following API:
*
* @ A constructor the accepts some, all, or none of the options above, and renders the widget
* @ A "refresh" function that can be called with some, all or none of the options above and will re-render the widget accordingly
*
* Note:
* - Use the default options as fallbacks, so not all options have to be provided to the ctor/refresh function
* - The widget must be a closed object so that several heatmaps can be generated on one page without affecting each-other!
* - You may not copy any existing heatmap implementation but it's ok to use one as reference!
* */

(function(w){

	// Configuration defaults
    var defaults = {
        lowColor: '#BEDB39',
        highColor: '#FF5347',
        dayClass: 'day',
        monthClass: 'month',
        year: new Date().getFullYear(),
        width: 1500,
        height: 200,
        cellSize: 15,
        container: 'body'
    }
	
	// This will be very useful... look at the API to see what they do!
	var day = d3.time.format("%w"),
        monthday = d3.time.format("%d"),
        month = d3.time.format('%m'),
        week = d3.time.format("%U"),
        percent = d3.format(".1%"),
        format = d3.time.format('%Y-%m-%dT00:00:00');
		
	// Constructor
	function Heatmap(options){
        // Implement me!
    }
	
	// The rest of the implementation is up to you :)
	
	widgets.Heatmap = Heatmap;

}(widgets))