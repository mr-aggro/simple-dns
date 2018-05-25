import socket, struct
import os


def make_ban():
    cmd = "curl -s https://raw.githubusercontent.com/zapret-info/z-i/master/dump.csv | cut -d ';' -f 1 |  tr '|' '\n' | grep '/' | tr -d ' ' | sort -k1 -n > ban_nets.txt"
    os.system(cmd)

def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def long2ip(long):
    """
    Convert an long string to IP
    """
    return socket.inet_ntoa(struct.pack('!L', long))


def check_rkn(ip, rkn):
    rkn_mask = int(rkn["mask"])
    rkn_ip = str(rkn["ip"])
    return (ip2long(ip) & (-1 << (32 - rkn_mask)) ) == ip2long(rkn_ip)


def razbor_net(cur_ip_adrr, ip_array):
    flag = False
    for cur_cidr in ip_array:
        if check_rkn(cur_ip_adrr, cur_cidr) is True:
            flag = True
    return flag

def get_dns_cahce():
    f = open("logs/super-puper.log", 'r')
    ret = []
    links = {}
    for i in f:
        if '#' in i:
            ret.append(i.split("#")[1:])
    f.close()
    import re
    host = re.compile('address=(.*) ttl=.*\'(.*)\'', re.IGNORECASE)
    for i in ret:
        for a in i:
            try:
                a = re.search(host, a)
                # print(a.group(1), a.group(2))
                links.setdefault(a.group(2), [])
                if a.group(1) not in links[a.group(2)]:
                    links.setdefault(a.group(2), []).append(a.group(1))
            except Exception:
                pass
    return links

if __name__=='__main__':
    # print("Get toxic net")
    # make_ban()
    # print("Got in ban_nets.txt")
    f = open('ban_nets.txt', 'r')
    rkn = []
    for net in f:
        rkn.append({"ip": net.split("/")[0], "mask": net.split("/")[1].replace("\n", "")})
    f.close()
    for_check = get_dns_cahce()

    f = open("hosts", 'w')
    for net in for_check.keys():
        print('Host: {}'.format(net))
        for ip in for_check.get(net):
            try:
                in_out = razbor_net(ip, rkn)
                if in_out is True:
                    print("       --> {}: BLOCKED".format(ip))
                else:
                    f.write('{} {}\n'.format(ip, net))
            except Exception:
                pass
    f.close()
