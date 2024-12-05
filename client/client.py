import socket, json
# Create a socket and connect to the server (IPV4) (TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cs:
    
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
    
# Ask the userto enter its name, and send it to the server
    user_name = input("Hi\n Enter your name: ").strip()  
    cs.sendall(user_name.encode('utf-8'))  

    print(f"Welcome {user_name}!\n")

# Define the main menu as a dictionary
    main_menu = {
        '1': 'headlines',
        '2': 'sources',
        '3': 'Quit'
    }

# Define the headlines sub menu as a dictionary
    Headlines = {
        '1': 'keywords',
        '2': 'category',
        '3': 'country',
        '4': 'all',
        '5': 'main'
    }

# Define the sources sub menu as a dictionary
    sources = {
        '1': 'category',
        '2': 'country',
        '3': 'language',
        '4': 'all',
        '5': 'main'
    }

    main_selection = 1
    while main_selection != 3: # Loop until the user chooses to quit
        print("Main menu:\n")

        for key, value in main_menu.items():
            print(f"{key}. {value}")

         # Get user selection from main menu
        main_selection = input("Select an option:").strip() 

        # Check if the selection is valid. if yes save its description, otherwise return an appropriate message
        if main_selection in main_menu:
            main_desc = main_menu[main_selection]
        else:
            print("Invalid selected number! Try again.")
            continue
        
        # If user selects 'Quit', close connection and exit
        if main_selection == '3':  
            cs.sendall(main_desc.encode('utf-8'))  
            print("Exiting... Goodbye")
            exit()

        # headlines submenu if user selects option 1
        if main_selection == '1': 

            for id, option in Headlines.items():
                print(f"{id} - {option}")

            # Get selection for headlines submenu
            Headlines_selection = input("Select your option:\n").strip() 

            if Headlines_selection in Headlines:
                Headlines_desc = Headlines[Headlines_selection]
            else:
                print("Invalid selected number! Try again please.")
                continue
            
            # If user selects 5 'main', break back to main menu
            if Headlines_selection == '5':  
                break

            # Construct request based on selected option
            elif Headlines_selection == '4':
                request=f"{main_desc},{Headlines_desc}"

            else:  
                value = input(f"Enter the {Headlines_desc} to search for:\n").strip() 
                request = f"{main_desc},{Headlines_desc},{value}"
                
        # sources submenu if user selects option 2
        elif main_selection == '2':  

            for id, option in sources.items():
                print(f"{id} - {option}")  

            # Get selection for sources submenu
            sources_selection = input("Select your option:\n").strip() 

            if sources_selection in sources:
                source_desc=sources[sources_selection]
            else:
                    print("Invalid selected number! Try again please.")
                    continue

            # If user selects 5 'main', break back to main menu
            if sources_selection == '5':  
                break

            # Construct request based on selected option
            elif sources_selection == '4':
                request=f"{main_desc},{source_desc}"

            else:
            
                value = input(f"Enter the {source_desc} to search for:\n").strip() 
                request = f"{main_desc},{source_desc},{value}"

         # Send the request to the server
        cs.sendall(request.encode('utf-8'))

        # Receive the server's response
        response = cs.recv(4096).decode('utf-8')
        # check if the response is JSON which means a valid category, or country, or language
        try:
            dict=json.loads(response)
            dict['back']='Back to the main menu' # Allow 'back' option to the user
            n=len(dict)

            # Print the articles
            print("Articles:\n")
            if main_selection == '2':
                print("Source name - author - title:")
            else:
                print("source name:")

            counter = 1  
            for article in dict:  
                if main_selection == '2':  # Headlines menu
                    print(f"{counter}. {article['name']} - {article['author']} - {article['title']}")

                elif main_selection == '1':  # sources menu
                    print(f"{counter}. {article['name']}")

                counter += 1

            print("\n",n,". Back to the main menu")
        # Otherwise: it is not a JSON response which means invalid category, or country, or language
        except json.JSONDecodeError:
            print(response)

        # Allow the user to select an article to provide its details or go back to the main menu
        article_selection=input("Select the number of desired detailed article: ").strip()
        if int(article_selection) == n:
            cs.sendall("back".encode('utf-8'))
            break
        else:
            cs.sendall(article_selection.encode('utf-8'))

        # Receive detailed response for the selected article
        try:
            detailed_response = cs.recv(4096).decode('utf-8')
            detailed_response_dict = json.loads(detailed_response)

            # Print detailed information for the selected article
            for key, value in detailed_response_dict[0].items():
                if key == "source" and "name" in value:
                    source_name = value["name"]
                    print("name:", source_name)
                else:
                    print(f"{key}: {value}")

        except json.JSONDecodeError:
            print(response)
