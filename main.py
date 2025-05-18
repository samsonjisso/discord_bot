from internet_checker import check_internet
from bot import run_discord_bot
import time

def main():
    while True:
        if check_internet():
            print("Internet is available. Starting the bot...")
            run_discord_bot()
            break
        else:
            print("No internet connection. Retrying after 20 minutes...")
            time.sleep(900)

if __name__ == "__main__":
    main()
