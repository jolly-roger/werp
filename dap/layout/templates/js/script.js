$(function(){
    {% if page == 'home' %}
        {% include 'js/home.js' %}
    {% elif page == 'check' %}
        {% include 'js/check.js' %}
    {% endif %}
});