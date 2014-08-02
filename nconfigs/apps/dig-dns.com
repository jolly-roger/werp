server {
    server_name dig-dns.com www.dig-dns.com;
    root /home/www/sisence-test;
    
    location / {
        index index.html;
    }
}