# Import necessary libraries
import collections
import os
import time
import statistics
from paho.mqtt import client as mqtt_publisher
from collections import defaultdict
import ntplib


# Define the MQTT topics to use for sending and receiving messages
topic_to_send_message = "ece/file_send"
topic_to_receive_message = "ece/time_recieve"

# Define the MQTT broker and topics to be used
BROKER_ADDRESS = '192.168.1.233'

# Initialize an NTP client and obtain the time offset
time_offset = ntplib.NTPClient().request('pool.ntp.org', version=3).offset

# Create dictionaries to store send and receive times for each file
time_to_send_file = defaultdict(list)
time_to_recieve_file = defaultdict(list)

def publish_file(publisher):
    # Define a dictionary to store the number of times each file will be transferred
    ftc = {
        '100B': 10000,
        '10KB': 1000,
        '1MB': 100,
        '10MB': 10
    }

    # Specify the path where the files are located
    path = 'DataFiles/'

    # Iterate through each file in the directory
    for file in os.listdir(path):
        with open(path+file, "rb") as f:
            # Obtain the size of the file and read its contents
            fsz = os.path.getsize(path+file)
            file_read = f.read(fsz)

            # Transmit the file the specified number of times
            for i in range(ftc[file]):
                if i%50 == 0:
                    print(i)
                # Record the send time of the file
                time_to_send_file[file].append(time.time() + time_offset)
                # Publish the file to the specified topic
                result = publisher.publish(topic=topic_to_send_message, payload=file_read, qos=1)
                result.wait_for_publish()
        print("sent ", file, " ", ftc[file], " times")

    # Transmit a message indicating the end of the file transfer
    result = publisher.publish(topic=topic_to_send_message, payload="end", qos=1)
    result.wait_for_publish()
    # print(result.is_published())
    print("end sent..")

def avg_calculation():
    # Define a dictionary to store the sizes of each file
    fns = {
        '100B': 100,
        '10KB': 10240,
        '1MB': 1048576,
        '10MB': 10320162,
    }

    # Calculate the time taken to transfer each file
    time_taken = collections.defaultdict(list)

    for k in time_to_send_file.keys():
        # print(k, " ", len(time_to_send_file[k]), " ", len(time_to_recieve_file[k]))
        # Compute the time taken to transfer each packet of the file
        file_send_times = sorted(time_to_send_file[k])
        file_received_times = sorted(time_to_recieve_file[k])
        time_taken[k] = []
        for x, y in zip(file_send_times, file_received_times):
            transfer_time = abs(x - float(y))
            throughput = fns[k] / transfer_time / 125
            time_taken[k].append(throughput)

    os.system("clear")
    print("\nResults: \n")
    for k in time_taken.keys():
        print("Mean", k, "\t\t = \t", statistics.mean(time_taken[k]))
        print("Standard Deviation", k, " = \t", statistics.stdev(time_taken[k]))
        print()

def active_message(client, userdata, msg):
    # Parse the message payload to obtain the file name and the time it was received
    file_name, received_time = msg.payload.decode().split(" ")
    # If the message indicates the end of the file transfer
    if file_name == "end":
        avg_calculation()
    else:
        time_to_recieve_file[file_name].append(received_time)

def run_mqtt_file_transfer_test():
    # Create a new MQTT client
    publisher = mqtt_publisher.Client()

    # mqtt_subscriber.username_pw_set(username="your_username", password="your_password")

    # Connect to the broker
    publisher.connect(BROKER_ADDRESS, keepalive=200)

    # Start the MQTT client in a separate thread so that it can run in the background
    publisher.loop_start()

    # Subscribe to the topic where the message with the file name will be received
    publisher.subscribe(topic_to_receive_message, qos=1)

    # Set the callback function that will be called when a message is received
    publisher.on_message = active_message

    # Publish the file to the broker
    publish_file(publisher)

    # Keep the script running indefinitely
    while True:
        continue

if __name__ == '__main__':
    os.system("clear")
    run_mqtt_file_transfer_test()