import socket, json
# Create a socket and connect to the server (IPV4) (TCP)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cs:
    cs.connect(("192.168.56.1", 5353))
# Ask the userto enter its name, and send it to the server
    user_name = input("Hi\n Enter your name: ").strip()  
    cs.sendall(user_name.encode('ascii'))  

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
            cs.sendall(main_desc.encode('ascii'))  
            print("Exiting... Goodbye")
            exit()

        # headlines submenu if user selects option 1
        if main_selection == '1': 

            while True:
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
                elif Headlines_selection == '1':  
                    keywords = input("Enter the keyword to search for:\n").strip() 
                    request = f"{main_desc},{Headlines_desc},{keywords}"
                      
                elif Headlines_selection == '2':  
                    category = input("Enter the category to search for:\n").strip()   
                    request = f"{main_desc},{Headlines_desc},{category}"
                    
                elif Headlines_selection == '3':  
                    country = input("Enter the country to search for:\n").strip() 
                    request = f"{main_desc},{Headlines_desc},{country}"
                
                elif Headlines_selection == '4':  
                    request = f"{main_desc},{Headlines_desc}"
                    
        # sources submenu if user selects option 2
        elif main_selection == '2':  

            while True:
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
                elif sources_selection == '1':
                    category = input("Enter the category to search for:\n").strip()   
                    request = f"{main_desc},{source_desc},{category}"

                elif sources_selection == '2':
                    country = input("Enter the country to search for:\n").strip() 
                    request = f"{main_desc},{source_desc},{country}"

                elif sources_selection == '3':
                    lan = input("Enter the language to search for:\n").strip() 
                    request = f"{main_desc},{Headlines_desc},{lan}"

                elif sources_selection == '4':
                    request = f"{main_desc},{source_desc}"

         # Send the request to the server
        cs.sendall(request.encode('ascii'))

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
            for key, value in dict.items():  
                print(f"\n{counter}. ")  
                counter += 1  

                # Print details of the article depending on the menu selection (headlines or sources)
                if main_selection == '2':
                    if key == 'name':
                        print(value, "-")
                    if key == 'author':
                        print(value, "-")
                    if key == 'title':
                        print(value)

                elif main_selection == '1':
                    if key == 'name':
                        print(value)

            print("\n",n,". Back to the main menu")
        # Otherwise: it is not a JSON response which means invalid category, or country, or language
        except json.JSONDecodeError:
            print(response)

        # Allow the user to select an article to provide its details or go back to the main menu
        article_selection=input("Select the number of desired detailed article: ").strip()
        if article_selection > n or article_selection < 1:
            print("Invalid selected number! Try again please.")
            continue
        elif article_selection == n:
            cs.sendall("back".encode('ascii'))
            break
        else:
            cs.sendall(article_selection.encode('ascii'))

        # Receive detailed response for the selected article
        detailed_response=cs.recv(4096).decode('utf-8')
        detailed_response_dict = json.loads(detailed_response)

        # Print detailed information for the selected article
        for key, value in detailed_response_dict.items():
            print(f"{key}: {value}")