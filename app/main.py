import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() # wait for client
    data = connection.recv(1024).decode("ISO-8859-1").split("\r\n\r\n")
    request_header = data[0].split("\r\n")
    request_line = request_header[0].split()
    request_target = request_line[1]
    if request_target == "/":
        connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif request_target.startswith("/echo/"):
        string = request_target.split("/")[-1]
        connection.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string)}\r\n\r\n{string}".encode("ISO-8859-1"))
    else:
        connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
