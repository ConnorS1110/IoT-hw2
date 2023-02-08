import os
import socket
import sys
import time

statsDict = {}

def main(files, num_of_times):
    HOST = '10.0.5.89'
    PORT = 8000

    data = b""

    for index, file in enumerate(files):
        print("Current file: ", file)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket created")
        except socket.error as e:
            print("Failed to create socket. Error code: " + str(e.errno) + " , Error message : " +
                                                                    e.strerror)
            sys.exit()
        # Connect to the server
        s.connect((HOST, PORT))

        # Request the file
        s.sendall(f"GET {file} NUM: {num_of_times[index]} HTTP/1.0\r\n\r\n".encode())

        startTime = time.time()
        # Receive the data
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            if b"END_OF_LOOP" in chunk:
                stopTime = time.time()
                updateStats(startTime, stopTime, data, file)
            else:
                data += chunk

        # Close the socket
        s.close()

def updateStats(startTime, stopTime, data, file):
    if file not in statsDict:
        statsDict[file] = {}
        statsDict[file]["n"] = 0
        statsDict[file]["listOfTimes"] = []
        statsDict[file]["totalTime"] = 0
        statsDict[file]["avg"] = 0
        statsDict[file]["std"] = 0
        statsDict[file]["data"] = 0
    statsDict[file]["n"] += 1
    statsDict[file]["listOfTimes"].append(round(stopTime - startTime, 3))
    statsDict[file]["totalTime"] += round(stopTime - startTime, 3)
    statsDict[file]["avg"] = round(statsDict[file]["totalTime"] / statsDict[file]["n"], 3)
    statsDict[file]["std"] = calcSTD(statsDict[file]["listOfTimes"], statsDict[file]["avg"], statsDict[file]["n"])
    statsDict[file]["data"] += len(data)

def calcSTD(listOfTimes, avg, n):
    sumOfDiffOfSquares = 0
    for currentTime in listOfTimes:
        sumOfDiffOfSquares += (currentTime - avg) ** 2

    return round((sumOfDiffOfSquares / n) ** 0.5, 3)

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)

    data_file_names = ["1MB", "10KB", "10MB", "100B"]
    times_to_send = []
    for index, file in enumerate(data_file_names):
        if file == "1MB":
            times_to_send.append(100)
        elif file == "10KB":
            times_to_send.append(1000)
        elif file == "10MB":
            times_to_send.append(10)
        else:
            times_to_send.append(10000)
    main(data_file_names, times_to_send)
    print(statsDict)
