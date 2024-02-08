import requests
import sys


def submit_payload(request_url, json_payload):
    try:
        response = requests.post(request_url, json=json_payload)
        response.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("Error: ", err)
        sys.exit(1)

    return response