if __name__ == "__main__":
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    
    context.load_cert_chain(certfile="path/to/your_cert.crt", keyfile="path/to/your_key.key")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cs:
        with context.wrap_socket(cs, server_hostname="localhost") as secure_socket:
            try:
                secure_socket.connect((get_local_ip(), 5353))
                
                if isinstance(secure_socket, socket.socket):
                    main(secure_socket)
            except ssl.SSLError as ssl_err:
                print(f"SSL Error: {ssl_err}")
            except KeyboardInterrupt:
                secure_socket.sendall("Quit".encode('utf-8'))
                print("Exiting... Goodbye")
                exit()
            except Exception as e:
                print(f"Error: {e}")