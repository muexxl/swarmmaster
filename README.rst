Welcome to SwarmMaster - an intelligent Access Point for rf24 clients on MAVLINK


Setup:

    Clients: Drones with nrf24 radios
    Master: Raspberry Pi with nrf24 radio 

Idea:
    Clients send data stream to RaspberryPi via nrf radio
    Raspberry reassembles the MAVLINK Messages and forwards them via UDP to the GroundControlStation
    Raspberry listens on UDP for MAVLINK Messages from GroundControlStation and forwards the Messages to the respective Client

    target_system is used to identify the respecive client.
    

Installation:

    git clone 

    cd swarmmaster
    pip install . 


Running:

    swarmmaster-run

IMPORTANT :

    use only ONE active network interface to avoid double reception of UDP broadcasts

    listening for broadcasts (RTCM messages !) on udp port 5544 

    listening for groundstation messages on udp port 14570
    publishing MAVLINK messages on udp port 14550