import subprocess
import csv
import os

REQUIRED_PACKAGES = ['cryptography', 'requests']

# Check if the required packages are installed
for package in REQUIRED_PACKAGES:
    try:
        __import__(package)
    except ImportError:
        # Package is not installed, so attempt to install it
        subprocess.check_call(['pip', 'install', package])

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from requests import post
from json import loads
import time
import sys
import requests

def clear_screen():
    # Clear screen
    print("\033[H\033[2J")

def encrypt_pnr(pnr):
    """Encrypts the PNR number using AES CBC encryption with PKCS7 padding.

    Args:
        pnr (str): The PNR number to encrypt.

    Returns:
        str: The base64-encoded encrypted PNR.

    """
    data = bytes(pnr, 'utf-8')
    backend = default_backend()
    padder = padding.PKCS7(128).padder()

    data = padder.update(data) + padder.finalize()
    key = b'8080808080808080'
    iv = b'8080808080808080'
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    enc_pnr = b64encode(ct)
    return enc_pnr.decode('utf-8')

def save_to_csv(pnr, json_data, csv_writer):
    """Saves the PNR status information to a CSV file.

    Args:
        pnr (str): The PNR number.
        json_data (dict): JSON data containing the PNR status information.
        csv_writer (csv.writer): CSV writer object.

    """
    try:
        boarding_station = json_data["BrdPointName"]
        destination_station = json_data["DestStnName"]
        quota = json_data["quota"]
        class_name = json_data["className"]
        train_number = json_data["trainNumber"]
        train_name = json_data["trainName"]
        date_of_journey = json_data["dateOfJourney"]

        for passenger in json_data["passengerList"]:
            passenger_serial_number = passenger["passengerSerialNumber"]
            current_status = passenger["currentStatus"]
            current_coach_id = passenger["currentCoachId"]
            current_berth_no = passenger["currentBerthNo"]
            csv_writer.writerow([
                pnr, boarding_station, destination_station, quota, class_name, train_number,
                train_name, date_of_journey, passenger_serial_number, current_status,
                current_coach_id, current_berth_no
            ])
    except KeyError as e:
        raise KeyError("Invalid JSON data format. Missing key: " + str(e))

def save_to_txt(pnr, json_data, txt_file):
    """Saves the PNR status information to a TXT file.

    Args:
        pnr (str): The PNR number.
        json_data (dict): JSON data containing the PNR status information.
        txt_file (file object): TXT file object.

    """
    try:
        boarding_station = json_data["BrdPointName"]
        destination_station = json_data["DestStnName"]
        quota = json_data["quota"]
        class_name = json_data["className"]
        train_number = json_data["trainNumber"]
        train_name = json_data["trainName"]
        date_of_journey = json_data["dateOfJourney"]

        txt_file.write(f"PNR: {pnr}\n")
        txt_file.write("PNR STATUS\n")
        txt_file.write("------------------------------------------------------------------\n")
        txt_file.write(f"{boarding_station} -> {destination_station}\n")  # source and destination station
        txt_file.write(f"{train_number} - {train_name}\n")  # train number and name
        txt_file.write("\n")
        txt_file.write(f"Quota: {quota}\n")
        txt_file.write(f"Journey Class: {class_name}\n")
        txt_file.write(f"Date Of Journey: {date_of_journey}\n")
        txt_file.write("\n")
        for passenger in json_data["passengerList"]:
            passenger_serial_number = passenger["passengerSerialNumber"]
            current_status = passenger["currentStatus"]
            current_coach_id = passenger["currentCoachId"]
            current_berth_no = passenger["currentBerthNo"]
            txt_file.write(
                f"Passenger {passenger_serial_number}: {current_status}/{current_coach_id}/{current_berth_no}\n"
            )
        txt_file.write("\n")
    except KeyError as e:
        raise KeyError("Invalid JSON data format. Missing key: " + str(e))

def print_pnr_data(json_data):
    """Prints the formatted PNR status information.

    Args:
        json_data (dict): JSON data containing the PNR status information.

    Raises:
        KeyError: If the required keys are missing in the JSON data.

    """
    try:
        boarding_station = json_data["BrdPointName"]
        destination_station = json_data["DestStnName"]
        quota = json_data["quota"]
        class_name = json_data["className"]
        train_number = json_data["trainNumber"]
        train_name = json_data["trainName"]
        date_of_journey = json_data["dateOfJourney"]

        print("PNR STATUS")
        print("------------------------------------------------------------------")
        print(f"{boarding_station} -> {destination_station}")  # source and destination station
        print(f"{train_number} - {train_name}")  # train number and name
        print()
        print(f"Quota: {quota}")
        print(f"Journey Class: {class_name}")
        print(f"Date Of Journey: {date_of_journey}")
        print()
        for passenger in json_data["passengerList"]:
            passenger_serial_number = passenger["passengerSerialNumber"]
            current_status = passenger["currentStatus"]
            current_coach_id = passenger["currentCoachId"]
            current_berth_no = passenger["currentBerthNo"]
            print(
                f"Passenger {passenger_serial_number}: {current_status}/{current_coach_id}/{current_berth_no}"
            )
    except KeyError as e:
        raise KeyError("Invalid JSON data format. Missing key: " + str(e))

def main():
    # Read PNR numbers from file
    try:
        with open('pnrs.txt', 'r') as file:
            pnrs = file.readlines()
    except FileNotFoundError:
        print("pnrs.txt file not found.")
        sys.exit(1)

    with open('pnr_status.csv', 'w', newline='') as csvfile, open('pnr_status.txt', 'w') as txtfile:
        csv_writer = csv.writer(csvfile)
        # Write CSV header
        csv_writer.writerow([
            'PNR', 'Boarding Station', 'Destination Station', 'Quota', 'Class', 'Train Number',
            'Train Name', 'Date of Journey', 'Passenger Serial Number', 'Current Status',
            'Current Coach ID', 'Current Berth No'
        ])
        
        for pnr in pnrs:
            pnr = pnr.strip()
            if len(pnr) != 10:
                print(f"PNR {pnr} LENGTH should be 10 DIGITS")
                continue

            encrypted_pnr = encrypt_pnr(pnr)

            json_data = {
                'pnrNumber': encrypted_pnr,
            }

            try:
                # Perform a POST request to the API endpoint with the encrypted PNR
                response = post('https://railways.easemytrip.com/Train/PnrchkStatus',
                                json=json_data,
                                verify=True)
                response.raise_for_status()
                json_data = loads(response.content)
                print(f"PNR : {pnr}")
            except (ConnectionError, TimeoutError,
                    requests.exceptions.RequestException) as e:
                print("An error occurred while connecting to the API:", str(e))
                continue
            except ValueError as e:
                print("Invalid response from the API. Response cannot be parsed as JSON.",
                      str(e))
                continue
            except Exception as e:
                print("An error occurred:", str(e))
                continue

            try:
                print_pnr_data(json_data)
                save_to_csv(pnr, json_data, csv_writer)
                save_to_txt(pnr, json_data, txtfile)
            except KeyError as e:
                print("An error occurred while parsing the API response:", str(e))
                continue

if __name__ == "__main__":
    main()
