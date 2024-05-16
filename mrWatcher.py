import ipaddress
import readline
import re
import netifaces
import os
import sqlite3
import subprocess
import socket
from scapy.all import srp, Ether, ARP
nameOfTheProject = ''
id_entry = 0

########### SYSTEM FUNCTIONS ##########
#Banner display
def banner():
    try:
        with open("banner.txt", "r") as file:
            banner = file.read()
            print(banner)
    except FileNotFoundError:
        print("o-o")
        print("mr Watcher")

def root_valid():
    if os.getuid() == 0 :
        pass
    else:
        print('no root session')
        os._exit(0)
#CLEAR-CONSOLE
def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')


#kinterrupt-menu
def kinterrupt():
    try:
        root_valid()
        clsq()
    except KeyboardInterrupt:
        print("user interruptiont")
        

#CLSQ
def clsq():
    try:
        while True:
            i = input("system init, clear terminal?[Y/N]: ")
            if (i=='y' or i=='Y'):
                clear_console()
                mainMenu()
            elif(i=='n' or i=='N'):
                mainMenu()
            else:
                print("no valid option")
    except KeyboardInterrupt:
        print('\n')
        print("user interruption...")


########### Networks configuration ##########

def get_mac_gateway(ip):
    try:
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        result, _ = srp(arp_request, timeout=3, verbose=False)        
        if result:
            gateway_mac = result[0][1].hwsrc
            return gateway_mac
        else:
            print("No MAC-address available.")
            return None
    except Exception as e:
        print("Error:", e)
        return None

#SHOW INTERFACES
 
def showInterface():
    interfaces = socket.if_nameindex()
    interfaces_ip = {}
    for idx, name in interfaces:
        try:
            ip = socket.if_indextoname(idx)
            interfaces_ip[name] = socket.gethostbyname(ip)
        except socket.error:
            pass
    return interfaces_ip




def get_network(ip, netmask):
    ip_address = ipaddress.IPv4Network(ip + '/' + netmask, strict=False)
    return str(ip_address) 

#GET INTERFACE NAME
def interface_get_info(interface):
    if_name = interface
    try: 
        commandResult = subprocess.check_output(['ifconfig',if_name]).decode()
        #machine ip
        lineIP = [line for line in commandResult.split('\n') if 'inet ' in line][0]
        ip = lineIP.split()[1]
        #mask
        mask = re.search(r'netmask (\S+)', commandResult).group(1)
        #network
        network = get_network(ip,mask)
        #ip-dg
        ip_gateway = subprocess.check_output(['ip','route','show','default']).decode().split()[2]
        ssid = input('ssid name: ')
        info_list = [ip,mask, network,ip_gateway,ssid]
        return info_list
    except Exception as e:
        print("ERROR: no interface detected")
        info_list = 'err'
        return info_list


################ DB MANAGE ###############

def exist_db(name):
    file_name = name + '.db'
    file_path = os.path.join('./.db', file_name)
    if os.path.isfile(file_path):
        opfi = input('A file with that name already exists, do you want to overwrite it? [Y|N] ') 
        if opfi == 'y' or opfi == 'Y':
            os.remove(file_path)
            return name
        elif opfi == 'n' or opfi =='N':
            print('Aborting creation of new-project')
            return None
            
    else:
        return name


#SET DB STORAGE PATH
def load_db(name):
    localName = name
    direct = './.db/'
    pathDBLoaded = str(os.path.abspath(direct))+'/'+str(name)+'.db'
    return pathDBLoaded
def create_db(name):
    id_entry = 0
    localName = name
    direct = './.db/'
    if not(os.path.exists(os.path.abspath(direct))):
        os.makedirs(os.path.abspath(direct))
    pathDB = str(os.path.abspath(direct))+'/'+str(name)+'.db'
    print("[*] project created in ", pathDB)
    con = sqlite3.connect(pathDB)
    cur = con.cursor()
    cur.execute("CREATE TABLE storage_IP(id INTEGER PRIMARY KEY,machine_ip, netmask, network, ip_dg, ssid)")
    con.commit()
    print("[*] table 'storage_IP' was created successfully.")
    cur.execute("CREATE TABLE network_summary(id INTEGER PRIMARY KEY, network, ssid)")
    print("[*] table 'network_summary' was created successfully.")
    con.commit()
    cur.execute("CREATE TABLE gateway(id INTEGER PRIMARY KEY, ipdg, macdg, ssid)")
    con.commit()
    print("[*] table 'gateway' was created successfully")
    con.close()
    print('')
    return pathDB


#CURRENT DB CONNECTOR
def connect_db(path_name):
    con = sqlite3.connect(path_name)
    return con    

#SHOW INTERFACES

############### system menu #########################



#SUB-MENU-CURRENT-PROJECT
def p_submenu_2(path_name, nameP):
    nameProject = nameP
    while(True):
        op = input("['{}']> ".format(nameProject))
        if op == 'cls' or op == 'clear':
            clear_console()
        if op == 'help' or op == 'Help' or op=='?':
            print("""
            add-info        add current interface info to database.
            delete-entry    delete an entry from db.
            show-main       show current main table
            show-networks   show current networks scanned
            show-gateway    show current gateway info
            show-interfaces show interfaces
            refresh         refresh interface state
            help            open help menu
            clear/cls       clear console
            exit-project    exit current project
        """)
        if op =='add-info':
            interface = str(input("choose an interface: "))
            info = interface_get_info(interface)
            if info == 'err':
                print('')
            else:
                add_current(path_name,info)
                add_current_brief(path_name,info)
                add_gateway(path_name,info)

        if op == 'show-networks':
            p_show_brief(path_name)
        if op == 'show-main':
            p_show(path_name)
        if op == 'show-gateway':
            p_show_gateway(path_name) 
        if op == 'exit-project':
            print('closing project - {}'.format(nameProject))
            stop = input("\npress any key to continue\n")
            break
        if op == 'delete-entry':
            id_value = input('select an  id: ')
            delete_entry(path_name,id_value)
        if (op == 'show-interfaces'):
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                try:
                    ip_address = netifaces.ifaddresses(interface)[netifaces.AF_INET]
                    for ip in ip_address:
                        ip_address = ip['addr']
                        print(f"""interface: <{interface}>
IP : {ip_address}
""")
                except KeyError:
                    pass
        if op == 'refresh':
            refresh_int()
            


#ADD CURRENT INTERFACE BRIEF
def add_gateway(path_name,info):
    global id_entry
    ids3= id_entry
    ip_gateway = info[3]
    ssid = info[4]
    mac = get_mac_gateway(ip_gateway)
    connect = connect_db(path_name)
    cur = connect.cursor()
    cur.execute(f"""
    INSERT INTO gateway(ipdg,macdg,ssid) VALUES
            ('{ip_gateway}','{mac}','{ssid}')""")
    connect.commit()
    connect.close()
def add_current_brief(path_name,info):
    global id_entry
    ids2 = id_entry
    network = info[2]
    ssid = info[4]
    conect = connect_db(path_name)
    cur = conect.cursor()
    cur.execute(f"""
    INSERT INTO network_summary(network,ssid) VALUES
             ('{network}','{ssid}')""")
    conect.commit()
    conect.close()

#ADD CURRENT INTERFACE INFO
def add_current(path_name,info):
    global id_entry
    id_entry += 1
    ids = id_entry
    ip = info[0]
    mask = info[1]
    network = info[2]
    ip_dg = info[3]
    ssid = info[4]
    conect = connect_db(path_name)
    cur = conect.cursor()
    cur.execute(f"""
        INSERT INTO storage_IP(machine_ip,netmask,network,ip_dg,ssid) VALUES
            ('{ip}','{mask}','{network}','{ip_dg}','{ssid}')""")
    conect.commit()
    conect.close()
    stop = input('Inserted successfully! ')

#DELETE AN ENTRY
def delete_entry(path_name,id_valor):
    connect = connect_db(path_name)
    cur = connect.cursor()
    query = "DELETE FROM storage_IP WHERE id = {}".format(id_valor)
    query2 = "DELETE FROM network_summary WHERE id = {}".format(id_valor)
    query3 = "DELETE FROM gateway WHERE id = {}".format(id_valor) 
    cur.execute(query)
    connect.commit()
    cur.execute(query2)
    connect.commit()
    cur.execute(query3)
    connect.commit()
    connect.close()
    print("Entry deleted")


def refresh_int():
    subprocess.run(['dhclient', '-r'])
    subprocess.run(['dhclient'])

#PROJECT-NAME CONSTRUCTOR
def p_name_load():
    nameOfLoad = str(input('Project name to load: '))
    file_name = nameOfLoad + '.db'
    file_path = os.path.join('./.db',file_name)
    return nameOfLoad

def p_name_recent():
    print(' ~~~ Available Projects ~~~')
    path = './.db/'
    content = os.listdir(path)
    for files in content:
        print(' - ',os.path.splitext(files)[0])


def p_name():
    nameOf = str(input("proyect-name: "))
    file_name = nameOf + '.db'
    file_path = os.path.join('./.db', file_name)
    if os.path.isfile(file_path):
        opfi = input('A file with that name already exists, do you want to overwrite it? [Y|N] ') 
        if opfi == 'y' or opfi == 'Y':
            os.remove(file_path)
            return nameOf   
        elif opfi == 'n' or opfi =='N':
            print('Aborting creation of new-project')
            return None
    else:
        return nameOf

#SHOW NETWORK DATABASE

def p_show_gateway(path_name):
    print("""
|  id  |    Gateway IP    |     MAC-Address      |      SSID              """)
    conect = connect_db(path_name)
    cur = conect.cursor()
    res = cur.execute("SELECT * FROM gateway")
    list_query = res.fetchall()
    if len(list_query) == 0:
        print("")
    else:
        for i, w in enumerate(list_query):
            idEntry = w[0]
            ipdg = w[1]
            mac = w[2]
            ssid = w[3]
            print(f'| {idEntry:3d}  |  {ipdg:15s} |  {mac:18s}  |  {ssid:28s}')
        conect.close()
        print('\n')
def p_show_brief(path_name):
    print("""
|  id  |       network      |            SSID             """)  
    conect = connect_db(path_name)
    cur = conect.cursor()
    res = cur.execute("SELECT * FROM network_summary")
    list_query = res.fetchall()
    if len(list_query) == 0:
        print("")
    else:
        for i, w in enumerate(list_query):
            idEntry = w[0] 
            nwork = w[1]
            ssid = w[2]
            print(f'| {idEntry:3d}  | {nwork:18s} | {ssid:28s} ') 
        conect.close()
        print('\n')

#SHOW DATABAE
def p_show(path_name):
    print("""
|  id  |      MachineIP    |      NetMask      |      Network      |     IP-dG     |              SSID      """)
    conect = connect_db(path_name)
    cur = conect.cursor()
    res = cur.execute("SELECT * FROM storage_IP")
    list_query = res.fetchall()
    if len(list_query) == 0:
        print("")
    else:
        for i, w in enumerate(list_query):
            id_entry = w[0]
            machine_ip = w[1]
            mask = w[2]
            network = w[3]
            ip_dg =  w[4]
            ssid =  w[5]
            print(f'| {id_entry:3d}  | {machine_ip:17s} | {mask:17s} | {network:17s} | {ip_dg:13s} | {ssid:32s} ')
    conect.close()
    print('\n')
    
    
####### SYSTEM-mainMenu #####

def mainMenu():
    banner()
    while(True):
        op = input("> ")
        if op == 'clear' or op =='cls':
            clear_console()
        if op== 'help' or op=='Help' or op=='?':
            print("""
            new-project         Start a new project (db, file, data)
            load-project        Open an existing project
            show-projects       Show all available projects
            help                Open help menu
            clear/cls           Clear console
            exit                Exit mr.Watcher
            """)
        if op=="exit":
            os._exit(0)
        if op=="new-project":
            nameOf = p_name()
            if nameOf == None:
                pass
            else:
                print("[*] creating project - {}".format(nameOf))
                pathdbs = create_db(nameOf)
                p_submenu_2(pathdbs,nameOf)

        if op == 'load-project':
            nameOf = p_name_load()
            print("[*] loading project - {}".format(nameOf))
            pathdbs = load_db(nameOf)
            p_submenu_2(pathdbs,nameOf)

        if op == 'show-projects':
            p_name_recent()
        else:
            pass
            





#while(True):
#        p_menu()
#        op = int(input("> "))
#        if (op == 1):
#            name = str(p_name())
#           pathdbs = create_db(name)
#           i = input("inWhileLoop")
#           p_show(pathdbs)
#           p_menu2(pathdbs)


if __name__ == "__main__":
    kinterrupt()
