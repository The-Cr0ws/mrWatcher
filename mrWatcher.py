import ipaddress
import readline
import re
import netifaces
import os
import sqlite3
import subprocess
import socket
from scapy.all import srp, Ether, ARP



# # # #----# # # # SYSTEM FUNCTION # # # #----# # # #

#BANNER-DISPLAY
def banner():
    try:
        with open("./.config/banner.txt", "r") as file:
            banner = file.read()
            print(banner)
    except FileNotFoundError:
        print("o-o")
        print("mr Watcher")

#KEYBOARD-INTERRUPT-EXCEPTION-ERROR
def kinterrupt():
    try:
        rootSession()
        clearScreenPrompt()
    except KeyboardInterrupt:
        print("User: KeyboardInterrupt")

def clearScreen():
    os.system("cls" if os.name == "nt" else 'clear')

def clearScreenPrompt():
    try:
        while True:
            i = input("Executing mr.Watcher, clear terminal? [Y/N]: ").strip()
            if (i == 'y' or i == 'Y'):
                clearScreen()
                mainMenu()
            elif (i == 'n' or i == 'N'):
                mainMenu()
            else:
                print("No valid option")
    except KeyboardInterrupt:
        print("\n")
        print("User: KeyboardInterrupt")

def rootSession():
    if os.getuid() == 0:            #MODIFY IN WINDOWS!
        pass
    else:
        print("No Root Session")
        os._exit(0)

# # # #----# # # # NETWORKS FUNCTION # # # #----# # # #

def reloadInterface():
    subprocess.run(['dhclient', '-r'])
    subprocess.run(['dhclient'])

def showInterfaces():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        try:
            ipAddress =  netifaces.ifaddresses(interface)[netifaces.AF_INET]
            for ip in ipAddress:
                address = ip['addr']
                print(f"""interface: <{interface}>
IP : {address}
""")
        except KeyError:
            pass

def getMacGateway(ipGateway):
    try:
        arpRequest = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ipGateway)
        result, _ = srp(arpRequest, timeout=3, verbose=False)
        if result:
            gatewayMac = result[0][1].hwsrc
            return gatewayMac
        else:
            print("No MAC-Address available")
            return None
    except Exception as e:
        print("Error: ", e)
        return None            

def getNetwork(ip,mask):
    networkAddress = ipaddress.IPv4Network(ip + '/' + mask, strict=False)
    return str(networkAddress)

def interfaceGetInfo(int):
    ifName = int
    try:
        #GET Machine's IP Address 
        commandResult = subprocess.check_output(['ifconfig',ifName]).decode()
        lineIP = [line for line in commandResult.split('\n') if 'inet ' in line][0]
        ip = lineIP.split()[1]
        #GET Machine's Network Mask
        networkMask = re.search(r'netmask (\S+)', commandResult).group(1)
        #GET Network information
        networkAddress = getNetwork(ip,networkMask)
        #GET Default Gateway's IP Address
        ipGateway = subprocess.check_output(['ip', 'route', 'show', 'default']).decode().split()[2]
        ssidName = input('SSID Name: ').strip()
        intInfo = [ip,networkMask,networkAddress,ipGateway,ssidName]
        return intInfo
    except Exception as e:
        return 'err'


# # # #----# # # # DATABASE MANAGEMENT# # # #----# # # #

def createDB(name):
    id_entry = 0
    relativePath = './.db/'
    if not(os.path.exists(os.path.abspath(relativePath))):
        os.makedirs(os.path.abspath(relativePath))
    pathDB = str(os.path.abspath(relativePath)) + '/' + str(name) + '.db'
    print("[*] Project created in ", pathDB)
    con = sqlite3.connect(pathDB)
    cur = con.cursor()
    cur.execute("CREATE TABLE storage_IP(id INTEGER PRIMARY KEY,machine_ip, netmask, network, ip_dg, ssid)")
    con.commit()
    cur.execute("CREATE TABLE network_summary(id INTEGER PRIMARY KEY, network, ssid)")
    con.commit()
    cur.execute("CREATE TABLE gateway(id INTEGER PRIMARY KEY, ipdg, macdg, ssid)")
    con.commit()
    con.close()
    print('')
    return pathDB

def loadDB(name):
    rPath = './.db/'
    pathDBLoaded = str(os.path.abspath(rPath))+'/'+str(name)+'.db'
    return pathDBLoaded

def connectDB(path):
    con = sqlite3.connect(path)
    return con

def addMainDB(path, info):
    ip = info[0]
    mask = info[1]
    network = info[2]
    ipGateway = info[3]
    ssid = info[4]
    connect = connectDB(path)
    cur = connect.cursor()
    cur.execute(f"""
        INSERT INTO storage_IP(machine_ip,netmask,network,ip_dg,ssid) VALUES
            ('{ip}','{mask}','{network}','{ipGateway}','{ssid}')""")
    connect.commit()
    connect.close()
    a = input("Network information was added succesfully ")

def addNetworkDB(path,info):
    network = info[2]
    ssid = info[4]
    connect = connectDB(path)
    cur = connect.cursor()
    cur.execute(f"""
    INSERT INTO network_summary(network,ssid) VALUES
             ('{network}','{ssid}')""")
    connect.commit()
    connect.close()


def addGatewayDB(path,info):
    ipGateway = info[3]
    ssid = info[4]
    macAddress = getMacGateway(ipGateway)
    connect = connectDB(path)
    cur = connect.cursor()
    cur.execute(f"""
    INSERT INTO gateway(ipdg,macdg,ssid) VALUES
            ('{ipGateway}','{macAddress}','{ssid}')""")
    connect.commit()
    connect.close()
    
def deleteEntry(path,idValue):
    connect = connectDB(path)
    cur = connect.cursor()
    query = "DELETE FROM storage_IP WHERE id = {}".format(idValue)
    query2 = "DELETE FROM network_summary WHERE id = {}".format(idValue)
    query3 = "DELETE FROM gateway WHERE id = {}".format(idValue) 
    cur.execute(query)
    connect.commit()
    cur.execute(query2)
    connect.commit()
    cur.execute(query3)
    connect.commit()
    connect.close()
    print(f"Entry {idValue} was deleted")
    
### ---- Show DBs ---- ####

def showGateway(path):
    print("""
|  id  |    Gateway IP    |     MAC-Address      |      SSID              """)
    conect = connectDB(path)
    cur = conect.cursor()
    res = cur.execute("SELECT * FROM gateway")
    listQuery = res.fetchall()
    if len(listQuery) == 0:
        print("")
    else:
        for i, w in enumerate(listQuery):
            idEntry = w[0]
            ipdg = w[1]
            mac = w[2]
            ssid = w[3]
            print(f'| {idEntry:3d}  |  {ipdg:15s} |  {mac:18s}  |  {ssid:28s}')
        conect.close()
        print('\n')

def showNetworks(path):
    print("""
|  id  |       network      |            SSID             """)  
    conect = connectDB(path)
    cur = conect.cursor()
    res = cur.execute("SELECT * FROM network_summary")
    listQuery = res.fetchall()
    if len(listQuery) == 0:
        print("")
    else:
        for i, w in enumerate(listQuery):
            idEntry = w[0] 
            nwork = w[1]
            ssid = w[2]
            print(f'| {idEntry:3d}  | {nwork:18s} | {ssid:28s} ') 
        conect.close()
        print('\n')

def showMainDB(path):
    print("""
|  id  |      MachineIP    |      NetMask      |      Network      |     IP-dG     |              SSID      """)
    connect = connectDB(path)
    cur = connect.cursor()
    res = cur.execute("SELECT * FROM storage_IP")
    listQuery = res.fetchall()
    if len(listQuery) == 0:
        print("")
    else:
        for i, w in enumerate(listQuery):
            idEntry = w[0]
            machineIp = w[1]
            mask = w[2]
            network = w[3]
            ipGateway =  w[4]
            ssid =  w[5]
            print(f'| {idEntry:3d}  | {machineIp:17s} | {mask:17s} | {network:17s} | {ipGateway:13s} | {ssid:32s} ')
    connect.close()
    print('\n')



# # # #----# # # # PROJECT CONSTRUCTOR # # # #----# # # # 

def availableProjects():
    print('Available Projects: ')
    path = './.db/'
    content = os.listdir(path)
    for files in content:
        print(' - ',os.path.splitext(files)[0])

def projectName():
    nameOfProject = str(input('Project name: ').strip())
    fileName = nameOfProject + '.db'
    filePath = os.path.join('./.db', fileName)
    if os.path.isfile(filePath):
        op = input('A file with that name already exists, Do you want to overwrite it? [Y/N]: ').strip()
        if op == 'y' or op == 'Y':
            os.remove(filePath)
            return nameOfProject
        elif op == 'n' or op == 'N':
            print(f'Creation of "{nameOfProject}" was cancelled')
            return 'ProjectCancelledByNotOverwrite'
    if not nameOfProject:
        return None            
    else:
        return nameOfProject

# # # #----# # # # MENU # # # #---# # # #

def projectMenu(path, pName):
    projectName = pName
    while(True):
        op = input(f"['{projectName}']> ").strip()
        if op == 'help' or op == 'Help' or op == '?':
            print("""
            add-info        add current interface info to database.
            delete-entry    delete an entry from db.
            show-main       show current main table
            show-networks   show current networks scanned
            show-gateway    show current gateway info
            show-interfaces show interfaces
            reload-intf     refresh interface state
            help            open help menu
            clear/cls       clear console
            exit-project    exit current project
         """)
        elif op == 'add-info':
            inf = str(input("Choose an interface: ").strip())
            infStatus = interfaceGetInfo(inf)
            if not inf:
                print("No interface was selected")
                pass
            else: 
                addMainDB(path, infStatus)
                addNetworkDB(path, infStatus)
                addGatewayDB(path, infStatus)
        elif op == 'delete-entry':
            idValue = input('Select an ID: ').strip()
            if idValue.isdigit():
                deleteEntry(path,idValue)
            else:
                print("Enter a numeric value")
                pass
        elif op == 'show-main':
            showMainDB(path)
        elif op == 'show-networks':
            showNetworks(path)
        elif op == 'show-gateway':
            showGateway(path)
        elif op == 'show-interfaces':
            showInterfaces()
        elif op == 'reload-intf':
            reloadInterface()
        elif op == 'cls' or op == 'clear':
            clearScreen()
        elif op =='exit-project':
            print('closing project "{}"'.format(projectName))
            stop = input("Press any key to continue\n")
            break
        elif op == '':
            pass
        else:
            print("Command not found. Type 'help' for assistance.")

def mainMenu():
    banner()
    while(True):
        op = input("> ").strip()
        if op == 'help' or op == 'Help' or op == '?':
            print("""
            new-project             Start a new project (db, file, data)
            open-project            Open an existing project
            show-projects           Show all available projects
            help                    Open help menu
            clear/cls               Clear console
            exit                    Exit mr.Watcher
            """)
        elif op == "new-project":
            nameOf = projectName()
            if nameOf == None:
                print("No name was especified")
                pass
            elif nameOf == 'ProjectCancelledByNotOverwrite':
                pass
            else:
                print("[*] Creating project - {}".format(nameOf))
                pathDBs = createDB(nameOf)
                projectMenu(pathDBs, nameOf)                #SECOND MENU
        elif op == "open-project":
            projectNameOpen = input('Enter project name to open: ').strip()
            try:
                with open(f"./.db/{projectNameOpen}.db", "r") as file:
                    print("[*] Loading project - {}".format(projectNameOpen))
                    pathDB = loadDB(projectNameOpen)
                    projectMenu(pathDB, projectNameOpen)
            except FileNotFoundError:
                print("Project not Found")
        elif op == 'show-projects':
            availableProjects()
        elif op == "clear" or op == "cls":
            clearScreen()
        elif op == "exit":
            os._exit(0)
        elif op == '':
            pass
        else:
            print("Command not found. Type 'help' for assistance.")
             

#EXECUTION
if __name__ == '__main__':
    kinterrupt()

