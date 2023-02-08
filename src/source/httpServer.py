import os
import socket
import sys

def main():
    HOST = ''
    PORT = 8000
    script_dir = os.path.dirname(__file__)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created successfully")
    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print('Bind failed. Error Code : ' + str(e.errno) + ' Message ' + e.strerror)
        sys.exit()
    print("Socket bind complete")
    s.listen(5)
    print("Socket is listening")
    while 1:
        c, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        recvDataSplit = c.recv(4096).decode('utf-8').split("GET ")[1].split(" HTTP/1.0\r\n\r\n")[0].split(" NUM: ")
        filePath = os.path.join(script_dir, "../../data/" + recvDataSplit[0])
        numTimesToSend = int(recvDataSplit[1])
        with open(filePath, "rb") as f:
            data = f.read() + b"END_OF_LOOP"
            for i in range(numTimesToSend):
                c.sendall(data)
        c.close()
        print("Connection closed")
    s.close()
    print("Socket closed")

if __name__ == "__main__":
    main()
