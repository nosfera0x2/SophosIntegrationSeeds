import socket
import time
import re
import random
import argparse
import requests
from datetime import datetime, timezone, timedelta

# Define the syslog server address and port
syslog_server_address = ('192.168.254.251', 10517)  # Update port if needed

# Function to update the timestamps in the syslog line to the current local time with timezone offset
def update_timestamps(syslog_line):
    # Find the number inside the angle brackets
    match = re.search(r'(<\d+>)', syslog_line)
    if match:
        prefix = match.group(1)
    else:
        prefix = "<12>"  # Default prefix if not found

    # Get the current local time and timezone
    current_time_local = datetime.now(timezone.utc).astimezone()
    local_timezone = current_time_local.strftime('%z')

    # Format the current time to match the original timestamp format with six-digit milliseconds
    current_time_local_str = current_time_local.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "{:03d}".format(current_time_local.microsecond // 1000) + local_timezone[:3] + ':' + local_timezone[3:]

    # Replace the old timestamp with the current time with offset
    syslog_line = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[-+]\d{2}:\d{2}', f'{current_time_local_str}', syslog_line)

    # Check for the additional time field and update if found
    time_field_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (AM|PM))', syslog_line)
    if time_field_match:
        current_time_str = current_time_local.strftime('%m/%d/%Y %I:%M %p')
        syslog_line = re.sub(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (AM|PM)', current_time_str, syslog_line)

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

# Function to replay syslog data
def replay_syslog_file(syslog_data):
    for syslog_line in syslog_data:
        updated_line = update_timestamps(syslog_line)

        # Send the syslog to the syslog server
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(updated_line.encode(), syslog_server_address)

        print(f"Sent: {updated_line}")

        random_sleep = random.randint(5, 15)
        time.sleep(random_sleep)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Replay syslog files.')
parser.add_argument('--file', help='Name of the syslog file to replay')
parser.add_argument('--all', action='store_true', help='Replay all syslog files')
args = parser.parse_args()

# URLs of the syslog data files
syslog_urls = {
    'veeam_encryption_password_deleted.txt': 'https://raw.githubusercontent.com/nosfera0x2/SophosIntegrationSeeds/main/veeam/veeam_encryption_password_deleted.txt',
    'veeam_encryption_password_modified.txt': 'https://raw.githubusercontent.com/nosfera0x2/SophosIntegrationSeeds/main/veeam/veeam_encryption_password_modified.txt',
    'veeam_mfa_disabled_global.txt': 'https://raw.githubusercontent.com/nosfera0x2/SophosIntegrationSeeds/main/veeam/veeam_mfa_disabled_global.txt',
    'veeam_ransomnote_detected.txt': 'https://raw.githubusercontent.com/nosfera0x2/SophosIntegrationSeeds/main/veeam/veeam_ransomnote_detected.txt',
}

# Replay all files if --all is specified
if args.all:
    for file_name, url in syslog_urls.items():
        print(f"Replaying syslog file: {file_name}")
        syslog_data = fetch_syslog_data(url)
        replay_syslog_file(syslog_data)
elif args.file:
    file_name = args.file
    if file_name in syslog_urls:
        print(f"Replaying syslog file: {file_name}")
        syslog_data = fetch_syslog_data(syslog_urls[file_name])
        replay_syslog_file(syslog_data)
    else:
        print("Invalid file name specified.")
else:
    print("No action specified
