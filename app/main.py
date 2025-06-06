import gzip
import os
import socket  # noqa: F401
import sys
import threading


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        connection, address = server_socket.accept() # wait for client
        threading.Thread(target=handle_requests, args=(connection,), daemon=True).start()

def handle_requests(connection):
    while True:
        data = connection.recv(1024)
        if data != b'':
            data = data.decode("ISO-8859-1").split("\r\n\r\n")
            request_header = data[0].split("\r\n")
            request_line = request_header[0].split()
            http_method = request_line[0]
            request_target = request_line[1]
            headers = request_header[1:]
            request_body = data[1]
            connection_close = "Connection: close\r\n" if "connection:close" in [x.lower().replace(": ", ":") for x in headers] else ""
            if request_target == "/":
                connection.sendall(f"HTTP/1.1 200 OK\r\n{connection_close}\r\n".encode("ISO-8859-1"))
            elif request_target.startswith("/echo/"):
                string = request_target.split("/")[-1].encode("ISO-8859-1")
                accept_encoding = next((x for x in headers if x.lower().startswith("accept-encoding:")), None)
                content_encoding = "Content-Encoding: gzip\r\n" if accept_encoding and "gzip" in [x.strip() for x in accept_encoding.split(":")[-1].split(",")] else ""
                if content_encoding != "":
                    string = gzip.compress(string)
                connection.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(string)}\r\n{content_encoding}{connection_close}\r\n".encode("ISO-8859-1") + string)
            elif request_target.startswith("/user-agent"):
                user_agent = next(x for x in headers if x.lower().startswith("user-agent:")).split(":")[-1].strip()
                connection.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n{connection_close}\r\n{user_agent}".encode("ISO-8859-1"))
            elif request_target.startswith("/files/"):
                filename = request_target.split("/")[-1]
                file = os.path.join(sys.argv[2], filename)
                if http_method == "GET":
                    try:
                        with open(file) as f:
                            data = f.read()
                            connection.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(data)}\r\n{connection_close}\r\n{data}".encode("ISO-8859-1"))
                    except:
                        connection.sendall(f"HTTP/1.1 404 Not Found\r\n{connection_close}\r\n".encode("ISO-8859-1"))
                else:
                    try:
                        with open(file, "w") as f:
                            f.write(request_body)
                            connection.sendall(f"HTTP/1.1 201 Created\r\n{connection_close}\r\n".encode("ISO-8859-1"))
                    except:
                        connection.sendall(f"HTTP/1.1 404 Not Found\r\n{connection_close}\r\n".encode("ISO-8859-1"))
            else:
                connection.sendall(f"HTTP/1.1 404 Not Found\r\n{connection_close}\r\n".encode("ISO-8859-1"))
            if connection_close != "":
                connection.close()
                break


if __name__ == "__main__":
    main()
