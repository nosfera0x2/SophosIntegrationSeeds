import socket
import time
import re
import requests
import random

# Define the syslog server address and port
syslog_server_address = ('sophosvirtualappliance_ip', sophosvirtualappliance_port)

# Function to update the timestamp in the syslog line
def update_syslog_line(syslog_line):
    current_time = time.strftime("%b %d %H:%M:%S")
    
    # Find the number inside the angle brackets and use it as the prefix
    match = re.search(r'<(\d+)>', syslog_line)
    prefix = f"<{match.group(1)}>" if match else "<165>"  # Use <165> as default if not found
    
    # Remove the original date and time, then add the new timestamp
    syslog_line = re.sub(r'^<\d+>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}', f'{prefix} {current_time}', syslog_line)
    
    return syslog_line

# Function to fetch syslog data from a URL
def fetch_syslog_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching syslog data: {e}")
        return []

# URL of the syslog data file on GitHub
syslog_data_url = 'https://raw.githubusercontent.com/nosfera0x2/fileZone/main/Darktrace-Grouped-Sept1.txt'

syslog_data = fetch_syslog_data(syslog_data_url)

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(syslog_server_address)  # Connect to the syslog server
    
    for syslog_line in syslog_data:
        updated_line = update_syslog_line(syslog_line)
        
        # Split the syslog data into separate lines and send each line separately
        lines_to_send = updated_line.split('\n')
        for line in lines_to_send:
            if line.strip():  # Skip empty lines
                # Send the syslog to the syslog server over TCP
                s.sendall(line.encode() + b'\n')  # Add a line break
                
                print(f"Sent: {line}")
        
        random_sleep = random.randint(60, 160)
        time.sleep(random_sleep)
