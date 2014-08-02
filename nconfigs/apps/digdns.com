server {
    server_name dig-dns.com www.dig-dns.com;
    
    location / {
        root /home/www/sisence-test;
        autoindex on;
    }
}