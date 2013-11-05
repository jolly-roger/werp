var domain_value = ''
var proxy_status_prefix = 'proxy_status_'

$(function(){
    function get_accessibility(){
        $.getJSON( "/get_10_checked?domain=" + domain_value, function(data){
            for (var i in data) {
                $('#' + proxy_status_prefix + data[i]['id']).
                    html('<span class="round label accessible_status">{% trans %}accessible_label{% endtrans %}</span>');
            }
        });
        $.getJSON( "/is_check_finished?domain=" + domain_value, function(data){
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
    
    $('#check_proxies_btn').click(function(){
        is_valid = false;
        domain_value = $('#domain_value').val()
        
        if(typeof(domain_value) == 'undefined' || domain_value == ''){
            alert('You should specify domain name or URL');
            return;
        }
        if(domain_value.match(/^http:\/\//gi) || domain_value.match(/^https:\/\//gi)){
            alert('Domain name or URL shouldn\'t start with "http://" or "https://"');
            return;
        }
        
        if(is_valid){
            $.post('/check_10', {domain: domain_value, jproxies: jproxies}, function(data){
                for (var i in proxies) {
                    proxy_status_td = $('#' + proxy_status_prefix + proxies[i]['id']);
                    proxy_status_td.
                        html('<span class="round label checking_status">{% trans %}checking_label{% endtrans %}</span>' +
                            '<img class="checking_progress" src="/images/checking.gif" alt="..." />');
                }
            });
        }
        
        setTimeout(get_accessibility, 1000);
    });
});