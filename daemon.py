import sys
import time
import queue
import socket
import struct
import ua_pb2
import ups_pb2
import requests
import threading
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

buff_len = 1024
sim_speed = 100000000

world_host = "10.236.48.21"
world_port = 12345

amazon_host = ""
amazon_port = 34567

request_pickup = "http://colab-sbx-pvt-10.oit.duke.edu:8000/apps/request_pickup"
search_truck = "http://colab-sbx-pvt-10.oit.duke.edu:8000/apps/search_truck"
arrive_warehouse = "http://colab-sbx-pvt-10.oit.duke.edu:8000/apps/arrive_warehouse"
request_deliver = "http://colab-sbx-pvt-10.oit.duke.edu:8000/apps/request_deliver"
finish_deliver = "http://colab-sbx-pvt-10.oit.duke.edu:8000/apps/finish_deliver"

q_non_prime = queue.Queue()
q_prime = queue.Queue()
l_on_pickup = []
l_on_delivery = []

def sendMsg(sock, message):
    serialMsg = message.SerializeToString()
    _EncodeVarint(sock.send, len(serialMsg))
    print(serialMsg)
    (length, pos) = _DecodeVarint32(serialMsg, 0)
    print("Message length: %s\nMessage start at %s" %(length, pos))
    sock.send(serialMsg)
    print("Command has sent")

def listenWorld(world_sock, amazon_sock):
    #listen to world response
    while(True):
        uresp = ups_pb2.UResponses()
        respMsg = world_sock.recv(buff_len)
        print(respMsg)
        (length, pos) = _DecodeVarint32(respMsg, 0)
        print("Message length: %s\nMessage start at %s" %(length, pos))
        uresp.ParseFromString(respMsg[pos:])
        print(uresp)
        if uresp.HasField("error"):
            print(uresp.error)
        elif len(uresp.delivered) != 0:
            #it's a per-deliver response
            print("into delivered...")
            #print(uresp)
        elif len(uresp.completions) != 0:
            #it's a completion response
            print("into completions...")
            for comp in uresp.completions:
                dic = {}
                dic["truck_id"] = comp.truckid
                dic["x"] = comp.x
                dic["y"] = comp.y
                if comp.truckid in l_on_pickup:
                    #it's a pickup completion
                    l_on_pickup.pop(l_on_pickup.index(comp.truckid))
                    response = requests.post(arrive_warehouse, json=dic)
                    resp_dic = response.json()
                    upsresponse = ua_pb2.UPSResponses()
                    upsresponse.resp_truck.truckid = resp_dic["truck_id"]
                    upsresponse.resp_truck.whnum = resp_dic["warehouse_id"]
                    upsresponse.resp_truck.shipid = resp_dic["tracking_id"]
                    serialMsg = sendMsg(amazon_sock, upsresponse)
                    #serialMsg = upsresponse.SerializeToString()
                    #print("=======Serialized message=======")
                    #print(serialMsg)
                    #_EncodeVarint(amazon_sock.send, len(serialMsg))
                    #amazon_sock.send(serialMsg)
                    #print("Command has sent")
                    #upsreparse = ua_pb2.UPSResponses()
                    #upsreparse.ParseFromString(serialMsg)
                    #print("=======Reparse UPSresponse=======")
                    #print(upsreparse)
                elif comp.truckid in l_on_delivery:
                    #it's a delivery completion
                    l_on_delivery.pop(l_on_delivery.index(comp.truckid))
                    response = requests.post(finish_deliver, json=dic)
                    resp_dic = response.json()
                    print("Truck %s delivery status: %s" %(comp.truckid, resp_dic["status"]))
                else:
                    print("Doesn't have truck %s's record" %(comp.truckid))
        else:
            print("Response format error!")

def connectToWorld(sock):
    uconnect = ups_pb2.UConnect()
    uconnected = ups_pb2.UConnected()
    uconnect.reconnectid = int(input("Enter reconnectid: "))
    sendMsg(sock, uconnect)
    respMsg = sock.recv(buff_len)
    print(respMsg)
    (length, pos) = _DecodeVarint32(respMsg, 0)
    print("Message length: %s\nMessage start at %s" %(length, pos))
    uconnected.ParseFromString(respMsg[pos:])
    print(uconnected)
    if uconnected.HasField("error"):
        return False
    else:
        return True

def goPickUp(sock, truck_id, wh_id):
    upickupcommand = ups_pb2.UCommands()
    upickup = upickupcommand.pickups.add()
    #upickup.truckid = int(input("Enter truck id: "))
    #upickup.whid = int(input("Enter warehouse id: "))
    upickup.truckid = truck_id
    upickup.whid = wh_id
    upickupcommand.simspeed = sim_speed
    upickupcommand.disconnect = False
    sendMsg(sock, upickupcommand)

def goDeliver(sock, dic):
    udelivercommand = ups_pb2.UCommands()
    udeliveries = udelivercommand.deliveries.add()
    udeliveries.truckid = dic["truck_id"]
    udeliverylocation = udeliveries.packages.add()
    udeliverylocation.packageid = dic["tracking_id"]
    udeliverylocation.x = dic["to_x"]
    udeliverylocation.y = dic["to_y"]
    sendMsg(sock, udelivercommand)

def truckSearch(sock):
    top = -1 #top records pending transaction ready to be picked up
    while(True):
        if top == -1:
            if not q_prime.empty():
                top = q_prime.get()
            elif not q_non_prime.empty():
                top = q_non_prime.get()
        if top != -1:
            response = requests.post(search_truck, json={"tracking_id":top})
            resp_dic = response.json()
            if resp_dic["truck_id"] != -1:
                l_on_pickup.append(resp_dic["truck_id"])
                goPickUp(sock, resp_dic["truck_id"], resp_dic["warehouse_id"])
                top = -1
        time.sleep(1)

def shipRequest(ship_detail):
    #parse ship_detail into dictionary
    dic = {}
    dic["ship_id"] = ship_detail.package.shipid
    dic["warehouse_id"] = ship_detail.package.whnum
    dic["x"] = ship_detail.x
    dic["y"] = ship_detail.y
    if ship_detail.HasField("upsAccount"):
        dic["upsAccount"] = ship_detail.upsAccount
    else:
        dic["upsAccount"] = ""
    dic["products"] = []
    for i in ship_detail.package.things:
        item = {}
        item["product_id"] = i.id
        item["count"] = i.count
        item["description"] = i.description
        dic["products"].append(item)
    print("=======package detail=======")
    print(dic)
     
    #send json to Django
    response = requests.post(request_pickup, json=dic)
    resp_dic = response.json()
    if resp_dic["is_prime"]:
        q_prime.put(resp_dic["tracking_id"])
    else:
        q_non_prime.put(resp_dic["tracking_id"])
    

def requestDeliverTruck(sock, truck_id):
    response = requests.post(request_deliver, json={"truck_id":truck_id})
    resp_dic = response.json()
    l_on_delivery.append(truck_id)
    goDeliver(sock, resp_dic)

if __name__ == '__main__':
    #socket with world as client
    try:
        world_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Can't create socket with world")
        sys.exit()
    world_sock.connect((world_host, world_port))
    print("Socket created")
    if not connectToWorld(world_sock):
        print("Connection to the world failed")
        sys.exit()

    #socket with amazon as server
    try:
        amazon_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Can't create socket with amazon")
        sys.exit()
    try:
        amazon_sock.bind((amazon_host, amazon_port))
    except socket.error as e:
        print(str(e))
    print("bind success")
    amazon_sock.listen(5)
    amazon_conn, amazon_addr = amazon_sock.accept()
    print(amazon_addr)    

    #create truck search thread
    t_truck_search = threading.Thread(target=truckSearch, args=(world_sock,))
    t_truck_search.start()

    #create world listen thread
    t_world_listen = threading.Thread(target=listenWorld, args=(world_sock,amazon_conn))
    t_world_listen.start()
    
    #listen to amazon for message AmazonCommands()
    while(True):
        acommands = ua_pb2.AmazonCommands()
        amazonRequestMsg = amazon_conn.recv(buff_len)
        print(amazonRequestMsg)
        (length, pos) = _DecodeVarint32(amazonRequestMsg, 0)
        print("Message length: %s\nMessage start at %s" %(length, pos))
        acommands.ParseFromString(amazonRequestMsg[pos:])
        
        if acommands.HasField("req_ship"):
            shipRequest(acommands.req_ship)
        elif acommands.HasField("req_deliver_truckid"):
            requestDeliverTruck(world_sock, acommands.req_deliver_truckid)
        else:
            print("Wrong message!")

