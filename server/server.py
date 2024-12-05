import re
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

# main thread
def search(sock):
    try:
        # recieve client name and print it
        client_name = sock.recv(1024).decode('utf-8')
        print(f"Connected to {client_name}")

        while True:
            # get a request from the client
            try:
                data = sock.recv(1024).decode('utf-8')
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
                response = response.get("articles", [])

            elif list == "sources":
                if option == 'all':
                    print(f"client {client_name} requested to search for all {list}")
                    value=''
                else:
                    value = data[2].strip()
                    print(f"client {client_name} requested to search for {list} by {option} ({value})")
                response = get_sources(option, value)
                response = response.get("sources", [])

            # send list if there is or send no result message
            if response:
                response = response[:15]  #only 15 results

                #prepare the list of headlines/sources
                prepared_list = []

                for x in response:
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

                #save the result in json file
                safe_client_name = re.sub(r'[^\w]', '_', client_name)
                file_name = f"{safe_client_name}_{list.replace(' ', '_')}-{option.replace(' ','_')}_B4.json"
                with open(file_name, 'w') as file:
                    json.dump(prepared_list, file, indent=4)
            
            else:
                sock.sendall("no result".encode('utf-8'))
                

            #getting client response after displaying the sources/headline list
            select = sock.recv(1024).decode('utf-8')

            # if the client did not choose a specific headline/source from the list
            if select == 'back':
                continue
            # return the article chosen by the client
            elif select.isdigit() and 1 <= int(select) <= len(response):
                sock.sendall(json.dumps(response[int(select) - 1]).encode('utf-8'))
            else:
                sock.sendall("invalid input/numper".encode('utf-8'))
                continue

    finally:
        #close the socket
        sock.close()
        print(f"disconnecting with {client_name}")

def main():
    # create a socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((get_local_ip(), 5353))
        server_socket.listen(3)
        print("Server is listening...")
    except Exception as e:
        print(f"Error starting server: {e}")
        return
        
    # loop to accept clients' connections
    client_count = 0
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