(function () {

    // Register utils namespace
    window.utils = window.utils || {};
	window.widgets = window.widgets || {};

    $(function () {
	
		// Create the widget
		var hm = new widgets.Heatmap({ container: '.chart', year: 2013 });

		$(this).find('#lowColor').val(hm.getDefaults().lowColor);
        $(this).find('#highColor').val(hm.getDefaults().highColor)
		
		// Load widget data
        $.get('data/sample.json').done(function (data) {

            /*
                Don't forget to run this app within a web server (such as IIS) otherwise, sample.json won't load.
                This project already comes with a web.config file that has the JSON MIME type.
                If you use a different web server, you might need to add the ".json" extension to your IIS MIME types yourself for this to work.
                It's OK to change the sample.json file to a different format but it must be loaded via an AJAX request, NOT attached as a .js file.
                You'll know you got it right when the line below works!
             */
			 
            //console.log(data);
			
			var formattedData = new utils.HeatYear().fromJSON(data.values); // You need to implement this - transform the data from the JSON request into something nicer for the widget to handle.

			// This will get the widget to re-render with colors!
            hm.refresh({data : formattedData});
        });
		
		
		// Refresh widget with new colors
		$('#colors').submit(function(){

            var low = $(this).find('#lowColor').val();
            var high = $(this).find('#highColor').val()

            hm.refresh({lowColor : low, highColor: high});

            return false;
        });   

    });

})();