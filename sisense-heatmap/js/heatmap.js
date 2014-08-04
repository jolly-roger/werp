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
        container: 'body',
		cellBorderColor: '#e6e6e6',
		data: {}
    }
	
	function mergeOptions(left, right){
		var opts = {};
		
		for(var option in left){
			opts[option] = option in right ? right[option] : left[option];
		}
		
		return opts;
	}
	
	// Constructor
	function Heatmap(options){
		var opts = mergeOptions(defaults, options);

		this.getDefaults = function(){
			return defaults;
		}
		
		this.refresh = function(options){
			if('data' in opts ||
			   (options.data && options.data.monthes.length && options.data.monthes.length &&
					options.data.monthes.length > 0)){
				opts = mergeOptions(opts, options);
				
				d3.select('svg').remove();
				
				var mWidth = 8 * opts.cellSize,
					curLine = 0,
					curWeek = 0,
					curMonth = 0
					maxValue = d3.max(opts.data.monthes, function (m){
						return d3.max(m.days, function(d){return d.value;})}),
					chart = d3.select(opts.container).append('svg').attr('width', opts.width).attr('height', opts.height).
						attr('transform', 'translate(20, 20)');
					heatColor = d3.scale.linear().
						domain([0, maxValue / 1.2, maxValue]).
						range([opts.lowColor, opts.highColor]);
					
				var ms = chart.selectAll('.month').data(opts.data.monthes).enter().append('g').
					attr('transform', function(m, i){return 'translate(' + (i * mWidth) + ', 20)';});
					// 20 is margin for chrome, should be found independent solution
				ms.append('text').
					text(function(m){return m.name;}).
						attr('x', function(){return mWidth / 2;}).
						attr('y', 0).
						attr("text-anchor", "middle").
						attr('class', 'month');
						
				var mFontSize = ms.select('text').node().getExtentOfChar(0);

				var ds = ms.selectAll('.day').data(function(m){return m.days;}).enter().
					append('rect').
						attr('x', function(d){return d.weekDay * opts.cellSize;}).
						attr('y', function(d, i){
							if(curMonth < d.month){
								curLine = 0;
								curMonth ++;
							}
							if(curWeek < d.week){
								curLine ++;
								curWeek ++;
							}
							return curLine * opts.cellSize + mFontSize.height;
						}).
						attr('class', 'day').
						attr('width', opts.cellSize).
						attr('height', opts.cellSize).
						style('stroke', opts.cellBorderColor).
						style('fill', opts.lowColor);
				ds.append('title').text(function(d){return d.tooltip;});
				ds.transition().duration(1000).
					style("fill", function(d){return heatColor(d.value);});
			}else{
				console.log('[Heatmap widget] refresh method: options.data or opts.data is empty');
			}
		}
    }
	
	// The rest of the implementation is up to you :)
	
	w.Heatmap = Heatmap;

}(widgets))