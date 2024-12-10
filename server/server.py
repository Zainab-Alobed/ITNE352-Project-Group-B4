import re
import socket
import json
import threading
import requests
import ssl
import os

"""  
savind API key and base url
"""
API_KEY = "4abb7da35b8346dfa7f1f20b5bc353e7"
BASE_URL = "https://newsapi.org/v2"

"""
for SSL/TLS we need to save the certificate and key paths
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(BASE_DIR, "../project.crt")
KEY_FILE = os.path.join(BASE_DIR, "../project.key")


def get_headlines(option, value):
    """
    This function is for getting headlined from the endpoint
    /top-headlines with specific criteria chosed by the client
    with the using of params
    """

    params = {"apiKey": API_KEY, "pageSize": 15}

    if option == "keywords":
        params["q"] = value
    elif option == "category":
        params["category"] = value
    elif option == "country":
        params["country"] = value

    try:
        response = requests.get(f"{BASE_URL}/top-headlines", params=params)
        if response.status_code != 200:
            """
            if code is not 200, then the request was not accepted
            """
            print(f"Error with API: {response.status_code}, {response.text}")
            return {"error": "API error"}
        return response.json()
    except Exception:
        return {"API_error": "API error, check the connection"}


# all headlines search function
def get_all_headlines():
    """
    All headlines have different endpoint which is /everything
    """
    params = {"apiKey": API_KEY, "pageSize": 15, "language": "en", "q": "news"}
    try:
        response = requests.get(f"{BASE_URL}/everything", params=params)
        if response.status_code != 200:
            print(f"Error with API: {response.status_code}, {response.text}")
            return {"error": "API error"}
        return response.json()
    except Exception:
        return {"API_error": "API error, check the connection"}


def get_sources(option, value):
    """
    getting the sources from endpoint /sources with the use of
    params to pass the API key and filtering criteria
    """
    params = {"apiKey": API_KEY, "pageSize": 15}

    if option == "category":
        params["category"] = value
    elif option == "country":
        params["country"] = value
    elif option == "language":
        params["language"] = value

    # get response from endpoint and return it
    try:
        response = requests.get(f"{BASE_URL}/sources", params=params)
        if response.status_code != 200:
            print(f"Error with API: {response.status_code}, {response.text}")
            return {"error": "API error"}
        return response.json()
    except Exception:
        return {"API_error": "API error, check the connection"}


def create_file(client_name, response, list, option):
    """
    ensre there is no space or special character in client name and file name
    and save the full API response into a json file
    """
    safe_client_name = re.sub(r"[^\w]", "_", client_name)
    file_name = (
        f"{safe_client_name}_{list.replace(' ', '_')}"
        f"-{option.replace(' ','_')}_B4.json"
    )
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(response, file, ensure_ascii=False, indent=4)


def handle_request(list, option, client_name, value=""):
    """
    Checking wether the client is looking for healdlines or
    sources list and communicate with the approprate function
    """
    if list == "headlines":
        if option == "all":
            print(f"client {client_name} requested to search for all {list}")
            full_response = get_all_headlines()
        else:
            print(
                f"client {client_name} requested to search for {list} by {option} ({value})"
            )
            full_response = get_headlines(option, value)
        response = full_response.get("articles", [])

    elif list == "sources":
        if option == "all":
            print(f"client {client_name} requested to search for all {list}")
        else:
            print(
                f"client {client_name} requested to search for {list} by {option} ({value})"
            )
        full_response = get_sources(option, value)
        response = full_response.get("sources", [])

    return response, full_response


def prepare_list(response, list):
    """
    Taking the list of articles/sources and
    prepare a list with only brief data for
    only 15 elements
    """
    response = response[:15]  # only 15 results
    prepared_list = []

    for x in response:
        if list == "headlines":
            prepared_list.append(
                {
                    "name": x["source"].get("name", "unknown"),
                    "author": x.get("author", "unknown"),
                    "title": x.get("title", "unkown"),
                }
            )

        else:
            prepared_list.append({"name": x.get("name", "unknown")})

    return prepared_list


def receive_complete_data(socket):
    buffer_size = 4096
    data = b""
    while True:
        part = socket.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break
    return data.decode("utf-8")


def search(sock):
    """
    This method is to handle connection with the clients
    """
    try:
        """
        recieve client name and print it
        """
        client_name = receive_complete_data(sock)
        print(f"New client connected {client_name}. Awating requests...")

        while True:
            """
            get requests from the clients and response to them within the loop
            """

            try:
                data = receive_complete_data(sock)
                data = data.split(",")

            except Exception as e:
                print(f"Error receiving or processing data: {e}")
                continue

            if data[0] == "Quit":
                break

            """
            split the request th know the exact option the client choosed
            """
            list = data[0].strip()  # resource or headline
            option = data[1].strip()  # search with what (category/language....)

            """ 
            get the list depending on the client choice headline/source
            """
            response, full_response = handle_request(
                list, option, client_name, data[2].strip() if 2 < len(data) else ""
            )

            """
            save the result in json file
            """
            create_file(client_name, full_response, list, option)

            """
            If failed to connect the the api and code was not 200
            """
            if "API_error" in full_response:
                sock.sendall(response["API_error"])
                continue

            """
            repare and send a list to respond, or send no result message
            """
            if response:
                prepared_list = prepare_list(response, list)
                sock.sendall(json.dumps(prepared_list).encode("utf-8"))

            else:
                sock.sendall("No results found. Please try agaim".encode("utf-8"))
                continue

            """
            After displaying the list to the user in the client, the 
            user will be able to select an element from the list
            to get the remaining details or he may mack to the main menue
            """
            select = receive_complete_data(sock).strip()

            if select == "Quit":
                break
            if select == "back":
                continue

            elif select.isdigit() and 1 <= int(select) <= len(response):
                """
                The condition ensure a valid select from user
                """
                sock.sendall(
                    json.dumps(response[int(select) - 1], ensure_ascii=False).encode(
                        "utf-8"
                    )
                )
            else:
                sock.sendall("Sorry! invalid selection.".encode("utf-8"))
                continue

    except Exception:
        print(f"Error in connetion with {client_name}")

    finally:
        # close the socket
        sock.close()
        print(f"Client {client_name} has disconnected.")


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

                # accepting connection from 5 clients
                while True:
                    sock, sockname = secure_socket.accept()
                    thread = threading.Thread(target=search, args=(sock,))
                    threads.append(thread)
                    thread.start()
                    client_count += 1
                    if client_count == 5:
                        break

                for thread in threads:
                    thread.join()

                print("Server is closing")
    except Exception as e:
        print(
            f"Error starting server: Please check the" " certificate and key files: {e}"
        )


if __name__ == "__main__":
    main()
