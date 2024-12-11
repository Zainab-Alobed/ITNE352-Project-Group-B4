import socket
import json
import ssl
import os
import re

# for SSL/TLS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(BASE_DIR, "../project.crt")
KEY_FILE = os.path.join(BASE_DIR, "../project.key")

def get_local_ip():
    try:
        hostname = "8.8.8.8"  # Google's public DNS server
        port = 80
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((hostname, port))
            ip_address = s.getsockname()[0]

        return ip_address
    
    except Exception as e:
        return f"Error retrieving IP: {e}"

"""
to follow up with recv(), to ensure all data sent over the socket is 
received completely
"""
def receive_complete_data(socket):
    buffer_size = 4096
    data = b""

    while True:
        part = socket.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break

    return data.decode("utf-8")

"""
Prompt the user to enter a valid name, and send it to the server.
If the user input is invalid, he/she will be prompted to try again 
until a valid name is entered.

parameters:
    cs: (socket)
"""
def get_user_name(cs):
    print("Hi!")
    while True:
        user_name = input("\nEnter your name (Only letters are allowed): ").strip()
        if re.match("^[a-zA-Z]+(?: [a-zA-Z]+)*$", user_name):
            break

        print("Invalid name. Only letters are allowed. Please try again.")

    cs.sendall(user_name.encode("utf-8"))
    print(f"Welcome {user_name}!\n")

""" 
This function define the main menu as a dictionary.
Then, get the user selection.

Returns:
    main_selection, main_desc
"""
def main_menu():
    main_menu = {"1": "headlines", "2": "sources", "3": "Quit"}
    while True:
        print("\nMain menu:")
        for key, value in main_menu.items():
            print(f"{key}. {value}")

        main_selection = input("Select an option: ").strip()

        if main_selection in main_menu:
            main_desc = main_menu[main_selection]
            break
        else:
            print("Invalid selected number! Try again.")

    return main_selection, main_desc

""" 
This function define the headlines sub menu as a dictionary.
Then, get the user selection.

Returns:
    Headlines_selection, Headlines_desc or -1,-1
"""
def Headlines_menu():
    Headlines = {
        "1": "keywords",
        "2": "category",
        "3": "country",
        "4": "all",
        "5": "main",
    }
    print("\n---- Headlines menu ----")
    for id, option in Headlines.items():
        print(f"{id} - {option}")

    Headlines_selection = input("\nSelect your option: ").strip()

    if Headlines_selection in Headlines:
        Headlines_desc = Headlines[Headlines_selection]
        return Headlines_selection, Headlines_desc
    else:
        print("Invalid selected number! Returning to main menu...")
        return -1, -1

""" 
This function define the sources sub menu as a dictionary.

Then, get the user selection.

Returns:
    sources_selection,source_desc or -1,-1
"""
def Sources_menu():
    sources = {
        "1": "category",
        "2": "country",
        "3": "language",
        "4": "all",
        "5": "main",
    }

    print("\n---- Sources menu ----")
    for id, option in sources.items():
        print(f"{id} - {option}")

    sources_selection = input("Select your option: ").strip()

    if sources_selection in sources:
        source_desc = sources[sources_selection]
        return sources_selection, source_desc
    else:
        print("Invalid selected number! Returning to main menu...")
        return -1, -1

"""
This function retrieves the server response.
If the reponse is valid json it displays the details.
otherwise, it displays an appropriate message.

parameter:
    cs: (socket)
    main_selection: The user's main menu selection ("1" for headlines, "2" 
    for sources).
"""
def response(cs, main_selection):
    try:
        # Check if the response is JSON which means a valid category, or country, or language
        response = receive_complete_data(cs)
        dict = json.loads(response)
        n = len(dict) + 1 # Allow 'back' to the main menu option to the user
        counter = 1
        
        for article in dict:
            if main_selection == "1":  # Headlines menu
                print(f"No. ({counter})")
                print(f"Source name: {article['name']} ")
                print(f"author: {article['author']} ")
                print(f"title: {article['title']} \n")
            elif main_selection == "2":  # sources menu
                print(f"No. ({counter})")
                print(f"Source name: {article['name']} \n")
            counter += 1
        print(f"{n}. Back to the main menu\n")

        return n
    
    # Otherwise: it is not a JSON response which means invalid category, or country, or language.
    # Print an appropriate message.
    except json.JSONDecodeError:
        print(f"{response}")
        return -1

""" 
This function receives detailed information form the server, and 
print it.

Parameters:
    cs: (socket)
    main_selection: The user's main menu selection ("1" for headlines, "2" 
    for sources).
    """
def detailed_response(cs, main_selection):
    try:
        detailed_response = receive_complete_data(cs)
        detailed_response_dict = json.loads(detailed_response)
        source_name = detailed_response_dict.get("source", {}).get(
            "name", "Unknown Source"
        )

        url = detailed_response_dict.get("url", "No URL")
        description = detailed_response_dict.get("description", "No Description")
        print("Source name: ", source_name)
        print("URL: ", url)
        print("Description: ", description)

        if main_selection == "1":
            author = detailed_response_dict.get("author", "Unknown Author")
            title = detailed_response_dict.get("title", "No Title")
            published_at = detailed_response_dict.get("publishedAt", "Unknown Date")

            # Handle date and time extraction
            if "T" in published_at:
                date, time = published_at.split("T")
                print("Publish date: ", date)
                print("Publish time: ", time)
            else:
                print("Published at: ", published_at)
            print("Author: ", author)
            print("Title: ", title)

        else:
            country = detailed_response_dict.get("country", "Unknown Country")
            category = detailed_response_dict.get("category", "Unknown Category")
            language = detailed_response_dict.get("language", "Unknown Language")
            print("Country: ", country)
            print("Category: ", category)
            print("Language: ", language)

    except json.JSONDecodeError:
        print(detailed_response)
        return -1

def connection(cs):
    try:
        get_user_name(cs)

        while True:
            main_selection, main_desc = main_menu()  
            if main_selection == "3":
                cs.sendall(main_desc.encode("utf-8"))
                print("Exiting... Goodbye")
                exit()

            if main_selection == "1":
                Headlines_selection, Headlines_desc = Headlines_menu()
                if Headlines_selection == -1: # Invalid user input
                    continue

                if Headlines_selection == "5": # Back to the main menu
                    continue

                elif Headlines_selection == "4":
                    request = f"{main_desc},{Headlines_desc}"
                else:
                    if Headlines_selection == "2":
                        print(
                            f"\nHere is suggestions that might help you with the valid {Headlines_desc}:\nbusiness, general, health, science, sports, technology"
                        )
                    elif Headlines_selection == "3":
                        print(
                            f"\nHere is suggestions that might help you with the valid {Headlines_desc}:\nau, ca, jp, ae, sa, kr, us, ma"
                        )

                    value = input(
                        f"\nEnter the {Headlines_desc} to search for: "
                    ).strip()
                    request = f"{main_desc},{Headlines_desc},{value}"

            elif main_selection == "2":
                sources_selection, source_desc = Sources_menu()
                if sources_selection == -1: # Invalid user input
                    continue

                if sources_selection == "5": # Back to the main menu
                    continue
                elif sources_selection == "4":
                    request = f"{main_desc},{source_desc}"
                else:
                    if sources_selection == "1":
                        print(
                            f"\nHere is suggestions that might help you with the valid {source_desc}:\nbusiness, general, health, science, sports, technology"
                        )
                    elif sources_selection == "2":
                        print(
                            f"\nHere is suggestions that might help you with the valid {source_desc}:\nau, ca, jp, ae, sa, kr, us, ma"
                        )
                    elif sources_selection == "3":
                        print(
                            f"\nHere is suggestions that might help you with the valid {source_desc}:\nar, en"
                        )

                    value = input(f"Enter the {source_desc} to search for: ").strip()
                    request = f"{main_desc},{source_desc},{value}"

            if 'request' in locals():
                cs.sendall(request.encode("utf-8"))
                n = response(cs, main_selection)

                if n == -1:
                    continue
                article_selection = input(
                    "Select the number of desired detailed article: "
                ).strip()

                if int(article_selection) == n:
                    cs.sendall("back".encode("utf-8"))
                    continue
                else:
                    cs.sendall(article_selection.encode("utf-8"))
                check_details = detailed_response(cs, main_selection)

                if check_details == -1:
                    continue

    except Exception as e:
        print("Error in connection with the server:", e)

def main():
    # Create an SSL context to configure the connection's security settings.
    context = ssl.create_default_context()

    context.check_hostname = False # Disable hostname verification
    context.verify_mode = ssl.CERT_NONE # Disables certificate verification
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    # Create a TCP socket using IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_s:
        with context.wrap_socket(client_s, server_hostname="myserver") as cs:
            try:
                cs.connect((get_local_ip(), 5353))

                if isinstance(cs, socket.socket):
                    connection(cs)

            # Handle SSL-related errors
            except ssl.SSLError as ssl_err:
                print(f"SSL Error: {ssl_err}")
            
             # Handle a user interrupt (Ctrl+C).
            except KeyboardInterrupt:
                cs.sendall("Quit".encode("utf-8"))
                print("Exiting... Goodbye")
                exit()

            # Catch and print any other exceptions that might occur during execution.
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()