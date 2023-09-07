import re
import datetime
import requests

# This only works on Fortinet Logs.

# Define a regular expression pattern to match the timestamp
pattern = r'[A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}'

# GitHub URL of the syslog file
github_url = 'https://raw.githubusercontent.com/nosfera0x2/fileZone/main/Fortinet-Grouped-Sept1.txt'

# Fetch the syslog data from the GitHub URL
response = requests.get(github_url)
if response.status_code == 200:
    syslog_data = response.text.split('\n')
else:
    print(f"Failed to fetch data from {github_url}")
    syslog_data = []

# Process the syslog data
for i, line in enumerate(syslog_data):
    # Find the timestamp within the syslog message
    match = re.search(pattern, line)

    if match:
        # Get the matched timestamp
        timestamp_str = match.group()

        # Get the current time in the format matching the syslog timestamp
        if i == 0:
            # Only modify the timestamp of the first line
            current_time = datetime.datetime.utcnow().strftime('%b %d %H:%M:%S')
        else:
            # Use the timestamp of the first line as a reference
            current_time = (datetime.datetime.utcnow() +
                            datetime.timedelta(seconds=i)).strftime('%b %d %H:%M:%S')

        # Replace the timestamp in the syslog line with the current time
        line = line.replace(timestamp_str, current_time, 1)

        # Extract the epoch timestamp from the syslog line
        epoch_str = line.split('FTNTFGTeventtime=')[1].split(' ')[0]

        # Get the current time as a datetime object
        current_datetime = datetime.datetime.utcnow()

        # Calculate the epoch timestamp in seconds (as an integer)
        epoch_seconds = int((current_datetime - datetime.datetime(1970, 1, 1)).total_seconds())

        # Convert epoch_seconds to nanoseconds
        current_time_ns = epoch_seconds * 1_000_000_000

        # Replace the epoch timestamp in the syslog line with the current time
        line = line.replace(epoch_str, str(current_time_ns))

    # Print or save the updated line as needed
    print(line)
