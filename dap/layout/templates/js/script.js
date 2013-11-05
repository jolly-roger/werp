var jproxies = '{{jproxies}}'
var proxies = eval(jproxies)
var domain_value = ''
var proxy_status_prefix = 'proxy_status_'

$(function(){
    function get_accessibility(){
        $.getJSON( "/get_10_checked?domain=" + domain_value, function(data){
            for (var i in data) {
                $('#' + proxy_status_prefix + data[i]['id']).
                    html('<span class="round label accessible_status">accessible</span>');
            }
        });
        $.getJSON( "/is_check_finished?domain=" + domain_value, function(data){
            if(!data){
                setTimeout(get_accessibility, 1000);
            }else{
                $('.checking_progress').each(function(){
                    $(this).parent().html('<span class="round label unaccessible_status">unaccessible</span>');
                });
            }
        });
    }
    
    $('#check_proxies_btn').click(function(){
        domain_value = $('#domain_value').val()
        $.post('/check_10', {domain: domain_value, jproxies: jproxies}, function(data){
            for (var i in proxies) {
                proxy_status_td = $('#' + proxy_status_prefix + proxies[i]['id']);
                proxy_status_td.
                    html('<span class="round label checking_status">checking</span>' +
                        '<img class="checking_progress" src="/images/checking.gif" alt="..." />');
            }
        });
        
        setTimeout(get_accessibility, 1000);
    });
});