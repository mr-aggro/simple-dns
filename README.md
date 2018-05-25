simple-dns
===========
A simple regular-expression based DNS server, based on twisted.

## Usage
hosts file modify after reading logs with dns_cache.py：  

    #IP            Domain
    127.0.0.1     www.alipay.com
    127.0.0.1     /.*?\.alipay\.com/

## Run

Server(127.0.0.1):

    sudo python dns.py
