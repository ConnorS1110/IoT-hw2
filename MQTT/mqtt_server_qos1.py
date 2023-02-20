# Import necessary libraries
import argparse
import collections
import os
import time
import statistics
from paho.mqtt import client as mqtt_publisher
from collections import defaultdict
import ntplib


parser = argparser.ArgumentParser()
parser.add_argument("file", help="filename to send")
parser.add_argument("count", help="number of times the file should be sent")

args = parser.parse_args()

# Define the MQTT topics to use for sending and receiving messages
topic_to_send_message = "ece/file_send"
topic_to_receive_message = "ece/time_recieve"

# Define the MQTT broker and topics to be used
BROKER_ADDRESS = '192.168.1.233'

# Initialize an NTP client and obtain the time offset
time_offset = ntplib.NTPClient().request('pool.ntp.org', version=3).offset

# Create dictionaries to store send and receive times for each file time_to_send = []
time_to_recieve = []

timestamps_missing = args.count

def publish_file(publisher):
    # Specify the path where the files are located
    path = args.file

    # Iterate through each file in the directory
    with open(path, "rb") as f:
        # Obtain the size of the file and read its contents
        file_read = f.read()
        args.size = len(file_read)

        # Transmit the file the specified number of times
        for i in range(args.count):
            if i%50 == 0:
                print(i)
            # Record the send time of the file
            time_to_send.append(time.time() + time_offset)
            # Publish the file to the specified topic
            result = publisher.publish(topic=topic_to_send_message, payload=file_read, qos=1)
            result.wait_for_publish()
    # print("sent ", file, " ", ftc[file], " times")
    print(f"sent {path} {args.count} times")


def avg_calculation():
    # Calculate the time taken to transfer each file
    time_taken = []

    # print(k, " ", len(time_to_send_file[k]), " ", len(time_to_recieve_file[k]))
    # Compute the time taken to transfer each packet of the file
    file_send_times = sorted(time_to_send)
    file_received_times = sorted(time_to_recieve)
    for x, y in zip(file_send_times, file_received_times):
        transfer_time = abs(x - float(y))
        throughput = args.size / transfer_time / 125
        time_taken.append(throughput)

    print("\nResults: \n")
    print("Mean", k, "\t\t = \t", statistics.mean(time_taken))
    print("Standard Deviation", k, " = \t", statistics.stdev(time_taken))
    print()


class _FinishReceiving(Exception):
    pass


def active_message(client, userdata, msg):
    # Parse the message payload to obtain the file name and the time it was received
    received_time = msg.payload.decode()
    # If the message indicates the end of the file transfer
    time_to_recieve.append(received_time)

    timestamps_missing -= 1
    if not timestamps_missing:
        raise _FinishReceiving()


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
    try:
        publisher.loop_forever()
    except _FinishReceiving:
        pass

if __name__ == '__main__':
    os.system("clear")
    run_mqtt_file_transfer_test()
