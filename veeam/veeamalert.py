import socket
import time
import re
import random
from datetime import datetime, timezone, timedelta

# Define the syslog server address and port
syslog_server_address = ('192.168.254.251', 10517)  # Update port if needed

# Function to update the timestamp in the syslog line to the current UTC time with CST offset
def update_timestamp(syslog_line):
    # Find the number inside the angle brackets
    match = re.search(r'(<\d+>)', syslog_line)
    if match:
        prefix = match.group(1)
    else:
        prefix = "<12>"  # Default prefix if not found

    # Get the current time in UTC
    current_time_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Convert UTC to CST
    cst_offset = timedelta(hours=-6)
    current_time_cst = current_time_utc.astimezone(timezone(cst_offset))

    # Format the current time to include milliseconds
    current_time_cst_str = current_time_cst.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    # Extract the existing timezone offset
    timezone_offset_match = re.search(r'([-+]\d{2}:\d{2})', syslog_line)
    if timezone_offset_match:
        existing_timezone_offset = timezone_offset_match.group(1)
    else:
        existing_timezone_offset = "-00:00"  # Default offset if not found

    # Include the timezone offset in the current time
    current_time_with_offset = current_time_cst_str + existing_timezone_offset

    # Replace the old timestamp with the current time with offset
    syslog_line = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[-+]\d{2}:\d{2}', f'{current_time_with_offset}', syslog_line)

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
