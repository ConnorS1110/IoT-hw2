import os
import sys
import time
import paho.mqtt.client as client
import ntplib
from collections import defaultdict


#topics
# Define the MQTT topics to use for sending and receiving messages
topic_to_send_message = "ece/file_send"
topic_to_receive_message = "ece/time_recieve"

#MQTT connection constants 
PORT_NUM = 1883
KEEP_ALIVE = 100

# Define the IP address of the MQTT broker to connect to
BROKER_ADDRESS = '192.168.1.233'

# Use NTP to get the current time and calculate an offset from UTC
time_offset = ntplib.NTPClient().request('pool.ntp.org', version=3).offset

# Create a defaultdict to store the times when messages were received, indexed by filename
received_time_file = defaultdict(list)

# Define a function to process incoming MQTT messages def active_message(client, userdata, msg):
    # Get the current time and add the time offset
    time_Received = time.time() + time_offset
    # Convert the received time to a string
    received_time = str(time_Received)
    # Get the payload of the message
    data = msg.payload
    # Assign a filename based on the size of the message
    size = sys.getsizeof(data)
    filename = (
        "end" if size < 50 else
        "100B" if size < 200 else
        "10KB" if size < 20000 else
        "1MB" if size < 2000000 else
        "10MB"
    )
    # If the filename is "end", print the contents of the received_time_file dictionary
    if filename == "end":
        print("files transferred")
    # Otherwise, append the received time to the list for the corresponding filename in the dictionary
    else:
        received_time_file[filename].append(time_Received)
    # Publish a message to the topic used for receiving messages, including the filename and received time
    client.publish(topic=topic_to_receive_message, payload=filename + " " + received_time, qos=1)

os.system("clear")

# Create an MQTT client instance
mqtt_subscriber = client.Client()

recv = 0
def new_sock_recv(self, bufsize):
    global recv
    ret = self.__sock_recv(bufsize)
    recv += len(ret)

mqtt_subscriber.__sock_recv = mqtt_subscriber._sock_recv
mqtt_subscriber._sock_recv = new_sock_recv

# Set the username and password for the broker if required
# mqtt_subscriber.username_pw_set(username="your_username", password="your_password")

# Connect to the broker
mqtt_subscriber.connect(BROKER_ADDRESS, port=PORT_NUM)

# Subscribe to the topic used for sending messages
mqtt_subscriber.subscribe(topic_to_send_message, qos=1)

# Define the callback function for incoming messages
def on_message_callback(client, userdata, message):
    # Call the active_message function with the incoming message
    active_message(client, userdata, message)

# Set the on_message callback function
mqtt_subscriber.on_message = on_message_callback

# Start the main loop to listen for incoming MQTT messages
mqtt_subscriber.loop_forever()

print(recv)
