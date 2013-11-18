//$(function(){
    $('#check_proxies_btn').click(function(){
        is_valid = true;
        domain_value = $('#domain_value').val()
        
        if(typeof(domain_value) == 'undefined' || domain_value == ''){
            alert('You should specify domain name or URL');
            is_valid = false;
        }
        if(domain_value.match(/^http:\/\//gi) || domain_value.match(/^https:\/\//gi)){
            alert('Domain name or URL shouldn\'t start with "http://" or "https://"');
            is_valid = false;
        }
        
        if(is_valid){
            window.location = '/check/' + domain_value;
        } 
    });
//});