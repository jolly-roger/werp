server {
    server_name dig-dns.com www.dig-dns.com;
    
    location / {
        alias /home/www/sisence-test/index.html;
        
    }
}