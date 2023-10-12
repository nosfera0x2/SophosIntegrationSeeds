import socket
import time
import re
import requests
import random

# Define the syslog server address and port
syslog_server_address = ('syslog_ip_address', port_number)

# Function to update the timestamp and FTNTFGTeventtime in the syslog line
def update_syslog_line(syslog_line):
    current_time = time.strftime("%b %d %H:%M:%S")
    current_time_ns = int(time.time() * 1e9)
    
    # Find the number inside the angle brackets
    match = re.search(r'(<\d+>)', syslog_line)
    if match:
        prefix = match.group(1)
    else:
        prefix = "<185>"  # Default prefix if not found
    
    # Remove the original date and time, then add the new timestamp
    syslog_line = re.sub(r'^<[0-9]+>[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}', f'{prefix}{current_time}', syslog_line)
    
    # Update the FTNTFGTeventtime
    ftntfgt_event_time_match = re.search(r'FTNTFGTeventtime=(\d+)', syslog_line)
    if ftntfgt_event_time_match:
        current_time_ns_str = str(current_time_ns)
        syslog_line = re.sub(r'FTNTFGTeventtime=\d+', f'FTNTFGTeventtime={current_time_ns_str}', syslog_line)
    
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
syslog_data_url = 'https://raw.githubusercontent.com/nosfera0x2/SophosIntegrationSeeds/main/Fortinet-Grouped-Sept1.txt'

syslog_data = fetch_syslog_data(syslog_data_url)
    
for syslog_line in syslog_data:
    updated_line = update_syslog_line(syslog_line)
        
    # Send the syslog to the syslog server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(updated_line.encode(), syslog_server_address)
        
    print(f"Sent: {updated_line}")
    
    random_sleep = random.randint(60,140)
    time.sleep(random_sleep)
