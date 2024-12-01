
import socket;
import json;
import threading
import requests
API_KEY="4abb7da35b8346dfa7f1f20b5bc353e7"
BASE_URL="https://newsapi.org/v2"

#headline search function
def get_headlines(option,value):
    #pass api key
    params={"apikey":API_KEY}
    if option=="1":
        params["q"]=value

    elif option == "2":
       params["category"] = value

    elif option == "3":
       params["country"] = value

    response = requests.get(f"{BASE_URL}/top-headlines", params=params)
    return response.json()
#more information about an article

#resource search function
def get_sources(option, value):
   #pass api key
   params = {"apiKey": API_KEY}
   if option == "category":
       params["category"] = value

   elif option == "country":
       params["country"] = value

   elif option == "language":
       params["language"] = value

   response = requests.get(f"{BASE_URL}/sources", params=params)
   return response.json()

#get local ip address
def get_local_ip():
   try:
       # Connect to an external server to get the local IP
       hostname = "8.8.8.8"  # Google's public DNS server
       port = 80
       with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
           s.connect((hostname, port))
           ip_address = s.getsockname()[0]
       return ip_address
   except Exception as e:
       return f"Error retrieving IP: {e}"


#main thread
def search(sock):
    client_name=sock.recv(1024).decode('ascii')
    print(f"client {client_name}")
    while true:
        option,value=sock.recv(1024).decode('ascii')
        #when the user quit 
        if option=='quit':
            break
        #divide the id to know which option list the client used 
        option=option.split('.')
        #for headline list
        if option[0] =='1':
            response=get_headlines(option[1],value)
            response=response.get("articles",[])
            if response:
                sock.sendall(response.encode('ascii'))
                select=sock.recv(1024).decode('ascii')
                if select=='back':
                    continue
                if 1<= int(select) <=len(response):
                    sock.sendall(response[int(select)-1].encode('ascii'))
            else:
                sock.sendall("no result".encode('ascii'))
                continue
        #for resources list
        elif option[0]==2:
            response=get_sources(option[1],value)
            response=response.get("articles",[])
            #send list if there is or send no result message
            if response:
                sock.sendall(response.encode('ascii'))
                select=sock.recv(1024).decode('ascii')
                if select=='back':
                    continue
                elif 1<= int(select) <=len(response):
                    sock.sendall(response[int(select)-1].encode('ascii'))
            else:
                sock.sendall("no result".encode('ascii'))
                continue
            
    sock.close()

def main():
    socket_s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket_s.bind((get_local_ip),49999)
    socket_s.listen(3)
    c=0
    while true:
        sock,sockname=socket_s.accept()
        thread=threading.Thread(target=search, args=(sock))
        thread.start()
        c+=1
        if(c==3):
            break

    print("Server is closing")
    socket_s.close()

if __name__=="__main__":
    main()
