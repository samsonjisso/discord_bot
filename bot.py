import discord
from discord.ext import commands
from discord import Interaction, app_commands
import json
from dotenv import load_dotenv
from os import getenv, path
import re
import logging
import io  # For in-memory file handling

load_dotenv()

# Load environment variables
TOKEN = getenv('TOKEN')

base_dir = path.dirname(path.abspath(__file__))  # Get the directory of the current script
vpnData_path = path.join(base_dir, "VPN_service_no.json")
internetServiceData_path = path.join(base_dir, "Internet_service_no.json")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_data(file_path):
    """Load JSON data from a file safely."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON from {file_path}: {e}")
        return {}

vpnData = load_json_data(vpnData_path)
internetServiceData = load_json_data(internetServiceData_path)

# Check if data is loaded
if not vpnData or not internetServiceData:
    logging.error("Failed to load VPN or Internet Service data")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)

def format_json_response(data):
    """Formats JSON data for sending as a message or file."""
    json_str = json.dumps(data, indent=2, default=str)
    if len(json_str) > 2000:  # Discord's message limit
        file = io.BytesIO(json_str.encode('utf-8'))  # Create in-memory file
        return discord.File(file, filename="services.json")
    return f"```json\n{json_str}\n```"

async def send_json_response(interaction: Interaction, data, title):
    """Handles sending large JSON responses efficiently."""
    response = format_json_response(data)
    if isinstance(response, discord.File):
        await interaction.response.defer()  # Defer to avoid timeout
        await interaction.followup.send(f"{title} data is too large. Sending as a file.", file=response)
    else:
        await interaction.response.send_message(f"{title}:\n{response}")

@bot.tree.command(name="vpn", description="Use vpn Command to find VPN Services")
@app_commands.describe(vpn="Enter VPN Service Name or Number")
async def vpn_command(interaction: Interaction, vpn: str):
    try:
        result_message = search_data(vpn, vpnData, "VPN")
        await interaction.response.send_message(result_message)
    except Exception as e:
        logging.error(f"Error handling vpn command: {e}")
        await interaction.response.send_message("🤷🏿❗An error occurred while processing the VPN command.")

@bot.tree.command(name="internet", description="Use internet command to find Internet Services")
@app_commands.describe(internet="Enter Internet Service Name or Number")
async def internet_command(interaction: Interaction, internet: str):
    try:
        result_message = search_data(internet, internetServiceData, "Internet Service")
        await interaction.response.send_message(result_message)
    except Exception as e:
        logging.error(f"Error handling internet command: {e}")
        await interaction.response.send_message("🤷🏿❗An error occurred while processing the Internet command.")

@bot.tree.command(name="all_vpn_services", description="Gets All VPN Services")
async def all_vpn_services(interaction: Interaction):
    try:
        await send_json_response(interaction, vpnData, "Here are all the VPN services")
    except Exception as e:
        logging.error(f"Error retrieving all VPN services: {e}")
        await interaction.response.send_message("🤷🏿❗An error occurred while fetching all VPN services.")

@bot.tree.command(name="all_internet_services", description="Gets All Internet Services")
async def all_internet_services(interaction: Interaction):
    try:
        await send_json_response(interaction, internetServiceData, "Here are all the Internet services")
    except Exception as e:
        logging.error(f"Error retrieving all Internet services: {e}")
        await interaction.response.send_message("🤷🏿❗An error occurred while fetching all Internet services.")

def normalize_string(s):
    """Normalize strings by removing non-alphanumeric characters and converting to lowercase."""
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

def search_data(user_input, data, data_type):
    """Search for a specific VPN or Internet service based on user input."""
    normalized_user_input = normalize_string(user_input)
    result = []

    try:
        user_input_number = float(user_input)
    except ValueError:
        user_input_number = None  # If conversion fails, it's not a number

    for service_number, details in data.items():
        try:
            address = details.get("address", "N/A")
            contact_name = details.get("contact", {}).get("name", "N/A")
            contact_phone_number = details.get("contact", {}).get("phone_number", "N/A")
            wan_ip_main = details.get("wan_ip", {}).get("main", "N/A")
            wan_ip_backup = details.get("wan_ip", {}).get("backup", "N/A")
            bb_type = details.get("bb_type", "N/A")
            tarif = details.get("tarif", "N/A")

            normalized_service_name = normalize_string(address)
            name_match = normalized_service_name.startswith(normalized_user_input)
            id_match = user_input_number is not None and user_input_number == float(service_number)

            if name_match or id_match:
                service_info = (
                    f"📌 {data_type} Service ➜ {address}\n"
                    f"📌 Service Number ➜ {service_number}\n"
                    f"🙎🏿 Contact Name ➜ {contact_name}\n"
                    f"☎️ Contact Number ➜ {contact_phone_number}\n"
                    f"🌐 Main WAN-IP ➜ {wan_ip_main}\n"
                    + (f"🌐 Backup WAN-IP ➜ {wan_ip_backup}\n" if wan_ip_backup != "N/A" else "")
                    + f"📶 Broadband Type ➜ {bb_type}\n"
                    f"💰 Tarif ➜ {tarif} birr\n"
                )
                result.append(service_info)

        except KeyError as e:
            logging.warning(f"Missing expected field {e} in service data.")
        except Exception as e:
            logging.error(f"Error processing service {service_number}: {e}")

    return "\n\n".join(result) if result else f"🤷🏿❗No {data_type} found for ➜ {user_input}"

@bot.event
async def on_ready():
    logging.info(f"{bot.user} is now running")

    try:
        await bot.tree.sync()
        logging.info("Global commands synced successfully.")
    except Exception as e:
        logging.error(f"Error syncing commands: {e}")

def run_discord_bot():
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.error(f"Error running the bot: {e}")
        raise
