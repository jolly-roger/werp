var proxy_status_prefix = 'proxy_status_'

function get_accessibility(){
    $.getJSON( "/get_checked?ses_key=" + ses_key + "&domain=" + domain, function(data){
        for (var i in data) {
            $('#' + proxy_status_prefix + data[i]['id']).
                html('<span class="round label accessible_status">{% trans %}accessible_label{% endtrans %}</span>');
        }
    });
    $.getJSON( "/is_finished?ses_key=" + ses_key + "&domain=" + domain, function(data){
        if(!data){
            setTimeout(get_accessibility, 1000);
        }else{
            $('.checking_progress').each(function(){
                $(this).parent().
                    html('<span class="round label unaccessible_status">{% trans %}unaccessible_label{% endtrans %}</span>');
            });
        }
    });
}

$.post('/run', {ses_key: ses_key, domain: domain_value, jproxies: jproxies}, function(data){
    for (var i in proxies) {
        proxy_status_td = $('#' + proxy_status_prefix + proxies[i]['id']);
        proxy_status_td.
            html('<span class="round label checking_status">{% trans %}checking_label{% endtrans %}</span>' +
                '<img class="checking_progress" src="/images/checking.gif" alt="..." />');
    }
});

setTimeout(get_accessibility, 1000);