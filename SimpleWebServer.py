import socket
import os.path

# Returns entire HTTP request as bytes.
#
# Current implementation will stall the server if HTTP request isn't formatted
# properly.
def read_http_request(client_socket):
    data_read = bytes()
    while True:
        data = client_socket.recv(2048)
        data_read += data
        if data_read[-4:] == b'\r\n\r\n':
            return data_read


# World's crappiest web server. Processes requests serially.
with socket.socket(family=socket.AF_INET, 
                   type=socket.SOCK_STREAM) as s:
    s.bind(('', 80))
    s.listen()
    print('Server is up and running')
    while True:
        (conn, addr) = s.accept()

        # For simplicity, only parse the path out of the HTTP request.
        with conn:
            http_request = read_http_request(conn)
            # Parse out the path.
            http_request_str = http_request.decode()
            path = http_request_str.split(' ')[1]
            # File path will be relative to this file.
            abs_path = 'index.html' if path == '/' else os.path.abspath('./' + path)
            # Retrieve the file at the given path. Otherwise return not found.
            try:
                with open(abs_path, 'r+b') as f:
                    response_content = f.read()
                    conn.send(b'HTTP/1.1 200 OK\r\n')
                    conn.send(b'\r\n')
                    conn.send(response_content)
            except FileNotFoundError:
                conn.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
