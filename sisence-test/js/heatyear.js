(function(u){
    function HeatYear() {
        var month = d3.time.format('%m'),
            week = d3.time.format('%U'),
            tooltip = d3.time.format('%a %m %d %Y');
        
        this.monthes = [
            {name:'January', days: []},
            {name:'February', days: [] },
            {name:'March', days: []},
            {name:'April', days: []},
            {name:'May', days: []},
            {name:'June', days: []},
            {name:'July', days: []},
            {name:'August', days: []},
            {name:'September', days: []},
            {name:'October', days: []},
            {name:'November', days: []},
            {name:'December', days: []}
        ];
        
        this.fromJSON = function(data){
            var i, day;
            
            if(data && data.length && data.length > 0){
                for(i=0; i < data.length; i++){
                    day = new Date(data[i][0].data);
                    
                    this.monthes[day.getMonth()].days[day.getDate() - 1] = {
                        "weekDay": day.getDay(),
                        "week": parseInt(week(day)),
                        "month": parseInt(month(day)) - 1,
                        "date": data[i][0].text,
                        "value":  data[i][1].data,
                        "tooltip": function(){return tooltip(day) + ': ' + data[i][1].text;}()
                    };
                }
            }else{
                console.log('[HeatYear utility] fromJSON method: data is empty');
            }
            
            return this;
        }
    }
    
    u.HeatYear = HeatYear
}(utils))