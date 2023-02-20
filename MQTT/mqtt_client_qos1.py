import argparse
import os
import sys
import time
import paho.mqtt.client as client
import ntplib
from collections import defaultdict


parser = argparse.ArgumentParser()
parser.add_argument("count", help="number of messages before termination")

args = parser.parse_args()


#topics
# Define the MQTT topics to use for sending and receiving messages
topic_to_send_message = "ece/file_send"
topic_to_receive_message = "ece/time_recieve"

#MQTT connection constants 
PORT_NUM = 1883
KEEP_ALIVE = 100

# Define the IP address of the MQTT broker to connect to
BROKER_ADDRESS = '192.168.1.198'

# Use NTP to get the current time and calculate an offset from UTC
time_offset = ntplib.NTPClient().request('pool.ntp.org', version=3).offset

# Create a defaultdict to store the times when messages were received, indexed by filename
received_times = []

recv_times = []

transfers_remaining = args.count

# Define a function to process incoming MQTT messages
def active_message(client, userdata, msg):
    global transfers_remaining
    # Get the current time and add the time offset
    time_Received = time.time() + time_offset
    # Convert the received time to a string
    received_time = str(time_Received)
    # Get the payload of the message
    data = msg.payload
    # Assign a filename based on the size of the message
    size = sys.getsizeof(data)

    # If the filename is "end", print the contents of the received_time_file dictionary
    transfers_remaining -= 1
    if not transfers_remaining:
        print("files transferred")
    # Otherwise, append the received time to the list for the corresponding filename in the dictionary
    else:
        received_times.append(time_Received)
    # Publish a message to the topic used for receiving messages, including the filename and received time
    # client.publish(topic=topic_to_receive_message, payload=filename + " " + received_time, qos=1)
    recv_times.append(received_time)

os.system("clear")

# Create an MQTT client instance
mqtt_subscriber = client.Client()

recv = 0
def new_sock_recv(self, bufsize):
    global recv
    ret = self.__sock_recv(bufsize)
    recv += len(ret)
    return ret

client.Client.__sock_recv = mqtt_subscriber._sock_recv
client.Client._sock_recv = new_sock_recv

# Set the username and password for the broker if required
# mqtt_subscriber.username_pw_set(username="your_username", password="your_password")

# Connect to the broker
mqtt_subscriber.connect(BROKER_ADDRESS, port=PORT_NUM)

# Subscribe to the topic used for sending messages
mqtt_subscriber.subscribe(topic_to_send_message, qos=1)

messages_received = 0

def print_recv_bytes():
    print(f"Total bytes received: {recv}", flush=True)

def send_recv_times():
    for t in recv_times:
        mqtt_subscriber.publish(topic=topic_to_receive_message, payload=t, qos=1)


class _FinishReceiving(Exception):
    pass


# Define the callback function for incoming messages
def on_message_callback(client, userdata, message):
    # Call the active_message function with the incoming message
    active_message(client, userdata, message)
    if not transfers_remaining:
        print_recv_bytes()
        send_recv_times()
        raise _FinishReceiving()


# Set the on_message callback function
mqtt_subscriber.on_message = on_message_callback

try:
# Start the main loop to listen for incoming MQTT messages
    mqtt_subscriber.loop_forever()
except _FinishReceiving:
    pass
