import ipaddress
import readline
import re
import netifaces
import os
import sqlite3
import subprocess
import socket
from scapy.all import srp, Ether, ARP

#Global Vars
nameOfTheProject = ''
id_entry = 0

# # # #----# # # # SYSTEM FUNCTION # # # #----# # # #

#BANNER-DISPLAY
def banner():
    try:
        with open("./.config/banner.txt", "r") as file:
            banner = file.reaad()
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
            i = input("Executing mr.Watcher, clear terminal? [Y/N]: ")
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

def interfaceGetInfo(int):
    ifName = int
    try:
        commandResult = subprocess.check_output(['ifconfig',ifName]).decode()
        lineIP = [line for line in commandResult.split('\n') if 'inet ' in line][0]
        ip = lineIP.split()[1]
        return ip
    except Exception as e:
        print("Error: Interface specified was not detected")
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


# # # #----# # # # PROJECT CONSTRUCTOR # # # #----# # # # 

def projectName():
    nameOfProject = str(input('Project name: ').strip())
    fileName = nameOfProject + '.db'
    filePath = os.path.join('./.db', fileName)
    if os.path.isfile(filePath):
        op = input('A file with that name already exists, Do you want to overwrite it? [Y/N]: ')
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
        op = input(f"['{projectName}']> ")
        if op == 'help' or op == 'Help' or op == '?':
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
        if op == 'add-info':
            inf = str(input("Choose an interface: ").strip())
            infStatus = interfaceGetInfo(inf)
            print(infStatus)
            if not inf:
                print("No interface was selected")
                pass
            else: 
                print("interface -ñ-ñ")
        if op == 'cls' or op == 'clear':
            clearScreen()


def mainMenu():
    banner()
    while(True):
        op = input("> ")
        if op == 'help' or op == 'Help' or op == '?':
            print("""
            new-project             Start a new project (db, file, data)
            load-project            Open an existing project
            show-projects           Show all available projects
            help                    Open help menu
            clear/cls               Clear console
            exit                    Exit mr.Watcher
            """)
        if op == "new-project":
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

        if op == "exit":
            os._exit(0)
             




#EXECUTION
if __name__ == '__main__':
    kinterrupt()

