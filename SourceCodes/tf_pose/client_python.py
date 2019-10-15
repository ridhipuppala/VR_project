#!/usr/bin/env python

import socket
import json


TCP_IP = '192.168.1.109'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "1.0,2.0,3.5"

backlog = 5 
size = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind((TCP_IP,TCP_PORT)) 
s.listen(backlog) 

while 1:
    client, address = s.accept() 
    print("Client connected.")
    client.sendall(MESSAGE)
    data =  client.recv(BUFFER_SIZE)
    print(data)

s.close