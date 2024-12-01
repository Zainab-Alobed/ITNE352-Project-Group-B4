import socket
import json
import threading
import requests

# API Key for NewsAPI
API_KEY = "4abb7da35b8346dfa7f1f20b5bc353e7"
#newaAPI link
BASE_URL = "https://newsapi.org/v2"

# headline search function
def get_headlines(option, value):
    # pass api key
    params = {"apiKey": API_KEY}

    #check choosen option
    if option == "1":
        params["q"] = value
    elif option == "2":
        params["category"] = value
    elif option == "3":
        params["country"] = value

    #get response from endpoint and return it 
    response = requests.get(f"{BASE_URL}/top-headlines", params=params)
    return response.json()

# resource search function
def get_sources(option, value):
    # pass api key
    params = {"apiKey": API_KEY}

    #check choosen option
    if option == "category":
        params["category"] = value
    elif option == "country":
        params["country"] = value
    elif option == "language":
        params["language"] = value

    #get response from endpoint and return it 
    response = requests.get(f"{BASE_URL}/sources", params=params)
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

# main thread
def search(sock):
    try:
        # recieve client name and print it
        client_name = sock.recv(1024).decode('utf-8')
        print(f"Client {client_name}")

        while True:
            # get a request from the client
            try:
                data = sock.recv(1024).decode('utf-8')
                op, value = data.split(',', 1)
                op = op.strip()
            except Exception as e:
                print(f"Error receiving or processing data: {e}")
                break
            #if client choosed to quit
            if op == 'quit':
                break
            
            #split the id th know the exact option the client choosed
            option = op.split('.')

            # for headline list
            if option[0] == '1':
                response = get_headlines(option[1], value)
                response = response.get("articles", [])

                # send list if there is or send no result message
                if response:
                    response = response[:15]  #send only 15 results
                    sock.sendall(json.dumps(response).encode('utf-8'))
                    select = sock.recv(1024).decode('utf-8')
                    # if the client did not choose a specific article from the list
                    if select == 'back':
                        continue
                    # return the article chosen by the client
                    elif select.isdigit() and 1 <= int(select) <= len(response):
                        sock.sendall(json.dumps(response[int(select) - 1]).encode('utf-8'))
                    else:
                        sock.sendall("invalid".encode('utf-8'))
                        continue
                else:
                    sock.sendall("no result".encode('utf-8'))
                    continue

            # for resources list
            elif option[0] == "2":
                response = get_sources(option[1], value)
                response = response.get("sources", [])
                # send list if there is or send no result message
                if response:
                    response = response[:15]  #send only 15 results
                    sock.sendall(json.dumps(response).encode('utf-8'))
                    select = sock.recv(1024).decode('utf-8')
                    # if the client did not choose a specific article from the list
                    if select == 'back':
                        continue
                    # return the article chosen by the client
                    elif select.isdigit() and 1 <= int(select) <= len(response):
                        sock.sendall(json.dumps(response[int(select) - 1]).encode('utf-8'))
                    else:
                        sock.sendall("invalid".encode('utf-8'))
                        continue
                else:
                    sock.sendall("no result".encode('utf-8'))
                    continue
            #save the result in json file
            file_name = f"{client_name.replace(' ', '_')}_{op.replace(' ', '_')}_B4.json"
            with open(file_name, 'w') as file:
                json.dump(response, file, indent=4)
    finally:
        #close the socket
        sock.close()

def main():
    # create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((get_local_ip(), 49999))
    server_socket.listen(3)
    print("Server is listening...")
    client_count = 0
    # loop to accept clients' connections
    while True:
        sock, sockname = server_socket.accept()
        thread = threading.Thread(target=search, args=(sock,))
        thread.start()
        # count for number of clients and stop the loop when it reaches 3
        client_count += 1
        if client_count == 3:
            break
        
    print("Server is closing")
    # close the socket
    server_socket.close()

if __name__ == "__main__":
   main()