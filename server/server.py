import re
import socket
import json
import threading
import requests
import ssl
import os

# API Key for NewsAPI
API_KEY = "4abb7da35b8346dfa7f1f20b5bc353e7"
#newaAPI link
BASE_URL = "https://newsapi.org/v2"
#for SSL/TLS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
CERT_FILE = os.path.join(BASE_DIR, "../project.crt")
KEY_FILE = os.path.join(BASE_DIR, "../project.key")


# headline search function
def get_headlines(option, value):
    # pass api key
    params = {"apiKey": API_KEY, "pageSize": 15}

    #check choosen option
    if option == "keywords":
        params["q"] = value
    elif option == "category":
        params["category"] = value
    elif option == "country":
        params["country"] = value

    #get response from endpoint and return it 
    response = requests.get(f"{BASE_URL}/top-headlines", params=params)
    if response.status_code != 200:
        print(f"Error with API: {response.status_code}, {response.text}")
        return {"error": "API error"}
    return response.json()

# resource search function
def get_sources(option, value):
    # pass api key
    params = {"apiKey": API_KEY, "pageSize": 15}

    #check choosen option
    if option == "category":
        params["category"] = value
    elif option == "country":
        params["country"] = value
    elif option == "language":
        params["language"] = value

    #get response from endpoint and return it 
    response = requests.get(f"{BASE_URL}/sources", params=params)
    if response.status_code != 200:
        print(f"Error with API: {response.status_code}, {response.text}")
        return {"error": "API error"}
    return response.json()

# get local ip address
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

def receive_complete_data(socket):
    buffer_size = 4096
    data = b""
    while True:
        part = socket.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break
    return data.decode('utf-8')

def create_file(client_name,response,list,option):
    #ensre there is no spase or special character in client name and file name
    safe_client_name = re.sub(r'[^\w]', '_', client_name)
    file_name = f"{safe_client_name}_{list.replace(' ', '_')}-{option.replace(' ','_')}_B4.json"
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(response, file, ensure_ascii=False, indent=4) 

# main thread
def search(sock):
    try:
        # recieve client name and print it
        client_name = receive_complete_data(sock)
        print(f"New client connected {client_name}. Awating requests...")

        while True:
            # get a request from the client
            try:
                data = receive_complete_data(sock)
                data = data.split(',')
                
            except Exception as e:
                print(f"Error receiving or processing data: {e}")
                continue
            #if client choosed to quit
            if data[0] == 'Quit':
                break
            
            #split the id th know the exact option the client choosed
            list=data[0].strip() #resource or headline
            option=data[1].strip() #search with what (category/language....)

            # get the list depending on the client choice headline/source
            if list == 'headlines':
                #endpoint for all headlines is defferent
                if option == 'all': 
                    print(f"client {client_name} requested to search for all {list}")
                    params = {"apiKey": API_KEY,
                               "pageSize": 15 ,
                               "language": "en",
                               "q": "news"
                               }
                    response = requests.get(f"{BASE_URL}/everything", params = params)
                    response = response.json()
                else:
                    value = data[2].strip()
                    print(f"client {client_name} requested to search for {list} by {option} ({value})")
                    response = get_headlines(option, value)
                res = response.get("articles", [])

            elif list == "sources":
                if option == 'all':
                    print(f"client {client_name} requested to search for all {list}")
                    value=''
                else:
                    value = data[2].strip()
                    print(f"client {client_name} requested to search for {list} by {option} ({value})")
                response = get_sources(option, value)
                res = response.get("sources", [])
            
            #save the result in json file
            create_file(client_name,response,list,option)

            # send list if there is or send no result message
            if res:
                res = res[:15]  #only 15 results

                #prepare the list of headlines/sources
                prepared_list = []

                for x in res:
                    if list == 'headlines':
                        prepared_list.append({
                            "name":x['source'].get('name','unknown'),
                            "author":x.get('author','unknown'),
                            "title":x.get('title','unkown')
                            })
                    
                    else: #sources
                        prepared_list.append({
                            "name":x.get('name','unknown')
                            })


                sock.sendall(json.dumps(prepared_list).encode('utf-8'))
            
            else:
                sock.sendall("No results found. Please try agaim".encode('utf-8'))
                continue
                

            #getting client response after displaying the sources/headline list
            select = receive_complete_data(sock).strip()

            # if the client did not choose a specific headline/source from the list
            if select == 'back':
                continue
            if select == 'Quit':
                break
            # return the article chosen by the client
            elif select.isdigit() and 1 <= int(select) <= len(res):
                sock.sendall(json.dumps(res[int(select) - 1], ensure_ascii=False).encode('utf-8'))
            else:
                sock.sendall("Sorry! invalid selection.".encode('utf-8'))
                continue

    finally:
        #close the socket
        sock.close()
        print(f"Client {client_name} has disconnected.")

def main():
    try:
        # craete SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        # create a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((get_local_ip(), 5353))
            server_socket.listen(3)
            print("Server is listening...")

            # Wrap the socket with SSL
            with context.wrap_socket(server_socket, server_side=True) as secure_socket:
                
                client_count = 0
                threads = []

                #accepting connection from 3 clients
                while True:
                    sock, sockname = secure_socket.accept()
                    thread = threading.Thread(target=search, args=(sock,))
                    threads.append(thread)
                    thread.start()
                    client_count += 1
                    if client_count == 3:
                        break
                    
                for thread in threads:
                    thread.join()
                    
                print("Server is closing")
    except Exception as e:
        print(f"Error starting server: Please check the certificate and key files: {e}")
if __name__ == "__main__":
   main()