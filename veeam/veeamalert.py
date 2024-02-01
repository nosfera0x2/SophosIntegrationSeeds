import socket
import time
import re
import random
from datetime import datetime

# Define the syslog server address and port
syslog_server_address = ('192.168.254.251', 10517)  # Update port if needed

# Function to update the timestamp in the syslog line
def update_timestamp(syslog_line):
    # Find the number inside the angle brackets
    match = re.search(r'(<\d+>)', syslog_line)
    if match:
        prefix = match.group(1)
    else:
        prefix = "<12>"  # Default prefix if not found
    
    # Extract the existing timestamp and timezone offset
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)-(\d{2}:\d{2})', syslog_line)
    
    if timestamp_match:
        # Extract the timestamp and timezone offset
        existing_timestamp = timestamp_match.group(1)
        existing_timezone_offset = timestamp_match.group(2)
        
        # Get the current datetime in the same format
        current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        
        # Replace the old timestamp with the current datetime
        syslog_line = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+-\d{2}:\d{2}', f'{current_datetime}-{existing_timezone_offset}', syslog_line)
    
    return syslog_line

# Function to read syslog data from a local file
def read_syslog_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().splitlines()
    except IOError as e:
        print(f"Error reading syslog file: {e}")
        return []

# Function to prompt the user for file selection
def select_syslog_file():
    print("Select a syslog file:")
    print("1. veeam_ransomnote_detected.txt")
    print("2. veeam_encryption_password_deleted.txt")
    print("3. veeam_encryption_password_modified.txt")
    print("4. veeam_mfa_disabled_global.txt")

    selection = input("Enter the number of your choice: ")

    file_mapping = {
        '1': 'veeam_ransomnote_detected.txt',
        '2': 'veeam_encryption_password_deleted.txt',
        '3': 'veeam_encryption_password_modified.txt',
        '4': 'veeam_mfa_disabled_global.txt',
    }

    selected_file = file_mapping.get(selection)

    if selected_file:
        return selected_file
    else:
        print("Invalid selection. Exiting.")
        exit()

# Choose the syslog file
selected_syslog_file = select_syslog_file()
syslog_data_path = f'{selected_syslog_file}'

syslog_data = read_syslog_file(syslog_data_path)
    
for syslog_line in syslog_data:
    updated_line = update_timestamp(syslog_line)
        
    # Send the syslog to the syslog server
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(updated_line.encode(), syslog_server_address)
        
    print(f"Sent: {updated_line}")
    
    random_sleep = random.randint(5, 15)
    time.sleep(random_sleep)
