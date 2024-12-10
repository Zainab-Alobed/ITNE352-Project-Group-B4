import socket
import json
import ssl
import os
import signal
import sys
import re


# for SSL/TLS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(BASE_DIR, "../project.crt")
KEY_FILE = os.path.join(BASE_DIR, "../project.key")


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


# to follow up with recv(), to ensure all data sent over the socket is received completely
def receive_complete_data(socket):
    buffer_size = 4096
    data = b""
    while True:
        part = socket.recv(buffer_size)
        data += part
        # Check if the received data is smaller than the buffer size.
        # Which indicates that there is no more data to be received.
        if len(part) < buffer_size:
            break
    return data.decode("utf-8")


def connection(cs):
    print("Hi!")
    # Ask the user to enter its name, and send it to the server
    while True:
        user_name = input("\nEnter your name (Only letters are allowed): ").strip()
        # Check if the name matches the regex (at least one letter)
        if re.match("^[a-zA-Z]+(?: [a-zA-Z]+)*$", user_name):
            break
        else:
            print("Invalid name. Only letters are allowed. Please try again.")

    cs.sendall(user_name.encode("utf-8"))

    print(f"Welcome {user_name}!\n")

    # Define the main menu as a dictionary
    main_menu = {"1": "headlines", "2": "sources", "3": "Quit"}

    # Define the headlines sub menu as a dictionary
    Headlines = {
        "1": "keywords",
        "2": "category",
        "3": "country",
        "4": "all",
        "5": "main",
    }

    # Define the sources sub menu as a dictionary
    sources = {
        "1": "category",
        "2": "country",
        "3": "language",
        "4": "all",
        "5": "main",
    }

    main_selection = "1"
    try:
        while main_selection != "3":  # Loop until the user chooses to quit
            print("\nMain menu:")
            for key, value in main_menu.items():
                print(f"{key}. {value}")

            # Get user selection from main menu
            main_selection = input("Select an option: ").strip()

            # Check if the selection is valid. if yes save its description, otherwise print an appropriate message
            if main_selection in main_menu:
                main_desc = main_menu[main_selection]
            else:
                print("Invalid selected number! Try again.")
                continue

            # If user selects 'Quit', close connection and exit
            if main_selection == "3":
                cs.sendall(main_desc.encode("utf-8"))
                print("Exiting... Goodbye")
                exit()

            # headlines submenu if user selects option 1
            if main_selection == "1":
                print("\n---- Headlines menu ----")
                for id, option in Headlines.items():
                    print(f"{id} - {option}")

                # Get selection for headlines submenu
                Headlines_selection = input("\nSelect your option: ").strip()

                if Headlines_selection in Headlines:
                    Headlines_desc = Headlines[Headlines_selection]
                else:
                    print("Invalid selected number! Try again please.")
                    continue

                # If user selects 5 'main', back to main menu
                if Headlines_selection == "5":
                    continue

                # Construct request based on selected option
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

            # sources submenu if user selects option 2
            elif main_selection == "2":
                print("\n---- Sources menu ----")
                for id, option in sources.items():
                    print(f"{id} - {option}")

                # Get selection for sources submenu
                sources_selection = input("Select your option: ").strip()

                if sources_selection in sources:
                    source_desc = sources[sources_selection]
                else:
                    print("Invalid selected number! Try again please.")
                    continue

                # If user selects 5 'main', back to main menu
                if sources_selection == "5":
                    continue

                # Construct request based on selected option
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

            # Send the request to the server
            cs.sendall(request.encode("utf-8"))

            # Receive the server's response
            response = receive_complete_data(cs)
            # Check if the response is JSON which means a valid category, or country, or language
            try:
                dict = json.loads(response)
                # Allow 'back' option to the user
                n = len(dict) + 1

                # Print the headlines/sources
                if main_selection == "1":
                    print("\nHeadlines:")
                else:
                    print("\nSources:")

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
            # Otherwise: it is not a JSON response which means invalid category, or country, or language.
            # Print an appropriate message.
            except json.JSONDecodeError:
                print(response)
                continue

            # Allow the user to select an article to provide its details or go back to the main menu
            article_selection = input(
                "Select the number of desired detailed article: "
            ).strip()
            if int(article_selection) == n:
                cs.sendall("back".encode("utf-8"))
                continue
            else:
                cs.sendall(article_selection.encode("utf-8"))

            # Receive detailed response for the selected article
            try:
                detailed_response = receive_complete_data(cs)
                detailed_response_dict = json.loads(detailed_response)

                # Print detailed information for the response
                source_name = detailed_response_dict.get("source", {}).get(
                    "name", "Unknown Source"
                )
                url = detailed_response_dict.get("url", "No URL")
                description = detailed_response_dict.get(
                    "description", "No Description"
                )
                print("Source name: ", source_name)
                print("URL: ", url)
                print("Description: ", description)

                if main_selection == "1":
                    author = detailed_response_dict.get("author", "Unknown Author")
                    title = detailed_response_dict.get("title", "No Title")
                    published_at = detailed_response_dict.get(
                        "publishedAt", "Unknown Date"
                    )

                    # Safely handle date and time extraction
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
                    category = detailed_response_dict.get(
                        "category", "Unknown Category"
                    )
                    language = detailed_response_dict.get(
                        "language", "Unknown Language"
                    )

                    print("Country: ", country)
                    print("Category: ", category)
                    print("Language: ", language)

            except json.JSONDecodeError:
                print(detailed_response)

    except Exception:
        print("Error in connection with the server")


def main():
    # Create an SSL context to configure the connection's security settings.
    context = ssl.create_default_context()

    context.check_hostname = False  # Disable hostname verification
    context.verify_mode = ssl.CERT_NONE  # Disables certificate verification
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

            # اandle a user interrupt (Ctrl+C).
            except KeyboardInterrupt:
                cs.sendall("Quit".encode("utf-8"))
                print("Exiting... Goodbye")
                exit()
            # Catch and print any other exceptions that might occur during execution.
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()