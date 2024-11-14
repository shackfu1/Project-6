import sys
import json
import math  # If you want to use math.inf for infinity

def ipv4_to_value(ipv4_addr):
    """
    Convert a dots-and-numbers IP address to a single 32-bit numeric
    value of integer type. Returns an integer type.
    """
    ipv4_addr = ipv4_addr.split(".")
    ipv4_addr = list(map(int,ipv4_addr))
    intval = (ipv4_addr[0] << 24) | (ipv4_addr[1] << 16) | (ipv4_addr[2] << 8) | ipv4_addr[3]
    return  intval

def get_subnet_mask_value(slash):
    """
    Given a subnet mask in slash notation, return the value of the mask
    as a single number of integer type. The input can contain an IP
    address optionally, but that part should be discarded.
    """
    slashnum = int(slash[slash.find("/")+1:len(slash)])
    mask = ((1 << slashnum) - 1) << (32-slashnum)
    return mask

def ips_same_subnet(ip1, ip2, slash):
    """
    Given two dots-and-numbers IP addresses and a subnet mask in slash
    notataion, return true if the two IP addresses are on the same
    subnet.

    Returns a boolean.
    """

    return ipv4_to_value(ip1) & get_subnet_mask_value(slash) == ipv4_to_value(ip2) & get_subnet_mask_value(slash)

def find_router_for_ip(routers, ip):
    """
    Search a dictionary of routers (keyed by router IP) to find which
    router belongs to the same subnet as the given IP.
    Return None if no routers is on the same subnet as the given IP.
    """

    for NewIp in routers:
        if ips_same_subnet(NewIp, ip, routers[NewIp]["netmask"]):
            return NewIp
    return None


def dijkstras_shortest_path(routers, src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """
    ToVisit = []
    distances = {}
    parents = {}
    ShortestPath = []
    ActualSrcIp = find_router_for_ip(routers, src_ip)
    ActualDestIP = find_router_for_ip(routers, dest_ip)

    for ip in routers:
        distances[ip] = 1000000000
        parents[ip] = None
        ToVisit.append(ip)
    distances[ActualSrcIp] = 0
    while ToVisit != []:
        current = None
        for ip in distances:
            if ip in ToVisit and (current == None or distances[ip] < distances[current]):
                current = ip
        #print(ToVisit)
        #print(ToVisit[ToVisit.index(current)])
        ToVisit.remove(current)
        for neighbor in routers[current]["connections"]:
            if neighbor in ToVisit:
                alt = distances[current] + routers[current]["connections"][neighbor]["ad"]
                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    parents[neighbor] = current
    Traversing = ActualDestIP
    while Traversing != None:
        ShortestPath.append(Traversing)
        Traversing = parents[Traversing]
    ShortestPath.reverse()
    if len(ShortestPath) == 1:
        ShortestPath = []
    return ShortestPath

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
