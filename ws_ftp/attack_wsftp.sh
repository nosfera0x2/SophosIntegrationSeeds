#!/bin/bash

# Prompt for the IP address
read -p "Enter the IP address: " ip_address

# Read the password from the session.enc file
payload=$(cat /home/ubuntu/attack_demos/ws_ftp/session.enc)

# Run the wsftp.py command
python3 wsftp.py -u $ip_address -p $payload
