# MQTT Implementation for File Transfer

This readme corresponds to MQTT implemetation for ECE 592.

The implementation was tested and executed on the following environment:

    Operating System: macOS Catalina Version 10.15.7
    Python version: 3.8.2

The following requirements must be fulfilled in order to execute the code:

    Python 3.8.2
    Paho-mqtt
    Wireshark
    Ntplib
    Mosquitto

## Procedure

The implementation requires three devices for running the code, one for running the publisher, one for running the subscriber and the other for running the broker.

To run the code for each QoS level, the following procedure needs to be followed:

    1. Start the broker by executing the command:
        /usr/local/sbin/mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf

    2. Update the IP address of the broker in the publisher and subscriber code.

    3. Start the Wireshark application to capture the MQTT packets at the publisher side.

    4. Run the subscriber by executing the command:

        python3 mqtt_client_qos_1.py
        or
        python3 mqtt_client_qos_2.py

    5. Run the publisher by executing the command:

        python3 mqtt_server_qos_1.py
        or
        python3 mqtt_server_qos_2.py

    6. Stop the Wireshark application after all the packets have been transferred.

        -   filter out MQTT packets and save the file as text format.
        -   find packets with Publish Message [ece/file_send]
        -   open TCP packets for published message 
        -   PDU size will contain the overhead of application layer
    
   

  
