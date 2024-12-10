def connection(cs):
    

    main_selection = "1"
    try:
        while main_selection != "3":  # Loop until the user chooses to quit
           

            

            # If user selects 'Quit', close connection and exit
            if main_selection == "3":
                cs.sendall(main_desc.encode("utf-8"))
                print("Exiting... Goodbye")
                exit()

            # headlines submenu if user selects option 1
            if main_selection == "1":
                

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
            # Print the headlines/sources
            if main_selection == "1":
                print("\nHeadlines:")
            else:
                print("\nSources:")

            # Receive the server's response
            response = receive_complete_data(cs)
           

            

    except Exception:
        print("Error in connection with the server")
