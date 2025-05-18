import socket
import requests

def check_internet():
    try:
        # Check connection to a known DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        
        # Attempt to fetch a known website to confirm actual internet access
        response = requests.get("http://www.google.com", timeout=5)
        if response.status_code == 200:
            return True
    except (OSError, requests.RequestException) as e:
        print(f"Error occurred: {e}")
        return False
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        exit()
    
    return False
