import socket
import time
import re
import random
from datetime import datetime, timedelta

# Define the syslog server address and port
syslog_server_address = ('192.168.254.251', 10517)  # Update port if needed
timezone_offset = -6  # Set your timezone offset in hours

# Function to update the timestamp in the syslog line
def update_timestamp(syslog_line):
    # Find the number inside the angle brackets
    match = re.search(r'(<\d+>)', syslog_line)
    if match:
        prefix = match.group(1)
    else:
        prefix = "<12>"  # Default prefix if not found
    
    # Extract the existing timestamp
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)-(\d{2}:\d{2})', syslog_line)
    
    if timestamp_match:
        # Extract the timestamp and timezone offset
        existing_timestamp = timestamp_match.group(1)
        existing_timezone_offset = timestamp_match.group(2)
        
        # Convert the existing timestamp to datetime object
        existing_datetime = datetime.strptime(existing_timestamp, '%Y-%m-%dT%H:%M:%S.%f')
        
        # Add the new timezone offset
        new_datetime = existing_datetime + timedelta(hours=timezone_offset)
        
        # Format the new timestamp
        new_timestamp = new_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        
        # Replace the old timestamp with the new one
        syslog_line = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+-\d{2}:\d{2}', f'{new_timestamp}-{existing_timezone_offset}', syslog_line)
    
    return syslog_line

# Function to read syslog data from a local file
def read_syslog_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().splitlines()
    except IOError as e:
        print(f"Error reading syslog file: {e}")
        return []

# Local path of the syslog data file
syslog_data_path = 'alert-veeam.txt'

syslog_data = read_syslog_file(syslog_data_path)
    
for syslog_line in syslog_data:
    updated_line = update_timestamp(syslog_line)
        
    # Send the syslog to the syslog server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(updated_line.encode(), syslog_server_address)
        
    print(f"Sent: {updated_line}")
    
    random_sleep = random.randint(5, 15)
    time.sleep(random_sleep)
