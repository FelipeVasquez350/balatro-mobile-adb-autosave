import re
import os
import time
import zlib
import logging
import datetime
from dotenv import load_dotenv
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen
from icmplib import ping
from icmplib.exceptions import NameLookupError
from sys import exit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Balatro Sync started.")

load_dotenv()
MOBILE_IP= os.getenv("MOBILE_IP","")
ADB_KEYS_PATH= os.getenv("ADB_KEYS_PATH","")
SAVE_PATH= os.getenv("SAVE_PATH","")
ALLOW_BACKUPS= bool(os.getenv("ALLOW_BACKUPS", False))
BACKUP_PATH= os.getenv("BACKUP_PATH","")



def init():
    success = False

    logger.info("Initializing")
    logger.info("Checking environment variables")

    if MOBILE_IP == None:
        logger.error("Please set the MOBILE_IP environment variable")
        exit(1)

    if SAVE_PATH and not os.path.exists(SAVE_PATH):
        logger.error(f"Game path does not exist at {SAVE_PATH}. Exiting.")
        exit(1)

    if ADB_KEYS_PATH and not os.path.exists(ADB_KEYS_PATH):
        logger.error("ADB keys path does not exist. Exiting.")
        exit(1)

    if not os.path.exists(f"{ADB_KEYS_PATH}/adbkey"):
        logger.error("Generating a public/private key pair")
        keygen(f"{ADB_KEYS_PATH}/adbkey")

    if ALLOW_BACKUPS and BACKUP_PATH and not os.path.exists(BACKUP_PATH):
        logger.error("Backup path does not exist. Exiting.")
        exit(1)

    while not success:
        if is_device_online(MOBILE_IP):
            try:
                if connect_device():
                    success = True
                else:
                    logger.info("Error connecting to device. Retrying...")
            except Exception as e:
                logger.error(f"Error: {e}")
        else:
            logger.info("Device not online. Retrying in 30 seconds")
            time.sleep(30)
    logger.info("Initialization complete")



def is_device_online(ip):
    try:
        host = ping(ip, count=5,  timeout=1, privileged=False)
    except NameLookupError:
        return False
    return host.packets_sent == host.packets_received



def connect_device():
    with open(f"{ADB_KEYS_PATH}/adbkey") as f:
        priv = f.read()
    with open(f"{ADB_KEYS_PATH}/adbkey.pub") as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)

    device = AdbDeviceTcp(MOBILE_IP, 5555, default_transport_timeout_s=9.0)
    device.connect(rsa_keys=[signer], auth_timeout_s=10)

    logger.info("Connected to the device")
    return device



def transfer_pc_to_mobile(profile: int):
    device = connect_device()

    logger.info("Transferring PC data to mobile")
    device.shell(f"mkdir /data/local/tmp/balatro")

    profile_files = f"{SAVE_PATH}/{profile}"

    for file in os.listdir(profile_files):
        logger.info(f"Pushing {file} to /data/local/tmp/balatro/{profile}/{file}")
        device.push(f"{profile_files}/{file}", f"/data/local/tmp/balatro/{profile}/{file}")

    logger.info("Pushing settings.jkr to /data/local/tmp/balatro/settings.jkr")
    device.push(f"{SAVE_PATH}/settings.jkr", "/data/local/tmp/balatro/settings.jkr")

    device.shell("am force-stop com.unofficial.balatro")
    device.shell(f"run-as com.unofficial.balatro cp -r /data/local/tmp/balatro/* ./files/save/game/")
    device.shell(f"rm -r /data/local/tmp/balatro/")

    logger.info("PC data transferred to mobile")
    return



def transfer_mobile_to_pc(profile: int):
    device = connect_device()

    files = (
        "settings.jkr",
        f"{profile}/profile.jkr",
        f"{profile}/meta.jkr",
        f"{profile}/save.jkr",
    )

    data = {}

    for file in files:
        data[file] = device.exec_out(f"run-as com.unofficial.balatro cat files/save/game/{file}", decode=False)

        if b"No such file or directory" in data[file]:
            continue

        try:
            if not os.path.exists(f"{SAVE_PATH}/{profile}"):
                os.makedirs(f"{SAVE_PATH}/{profile}")
                logger.info(f"Creating directory {SAVE_PATH}/{profile}")
            with open(f"{SAVE_PATH}/{file}", "wb") as f:
                f.write(data[file])
                logger.error(f"Writing file {SAVE_PATH}/{file}")
        except Exception as e:
            logger.info("Error writing file:", e)

    logger.info("Mobile data transferred to PC")
    return



def backup_pc():
    if ALLOW_BACKUPS == False:
        return True

    if os.path.exists(BACKUP_PATH):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.mkdir(f"{BACKUP_PATH}/PCBackup-{current_date}")

        os.system(f"cp -r {SAVE_PATH}/* {BACKUP_PATH}/PCBackup-{current_date}/")

        logger.info("PC data backed up")
        return True
    else:
        logger.error("Backup path does not exist")
    return False



def backup_mobile():
    if ALLOW_BACKUPS == False:
        return True

    if os.path.exists(BACKUP_PATH):
        device = connect_device()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.mkdir(f"{BACKUP_PATH}/MobileBackup-{current_date}")

        # Credit at https://gist.github.com/vanchaxy/5a9915cbeae2d95a52f671b4502a0f6d for making me discover the existence `exec_out` and this easier way to pull files
        files =  [
            "settings.jkr",
            "1/profile.jkr",
            "1/meta.jkr",
            "1/save.jkr",
            "2/profile.jkr",
            "2/meta.jkr",
            "2/save.jkr",
            "3/profile.jkr",
            "3/meta.jkr",
            "3/save.jkr",
        ]

        data = {}

        for file in files:
            data[file] = device.exec_out(f"run-as com.unofficial.balatro cat files/save/game/{file}", decode=False)

            if b"No such file or directory" in data[file]:
                continue

            try:
                dir = file.split("/")[0]
                if dir.isdigit() and not os.path.exists(f"{BACKUP_PATH}/MobileBackup-{current_date}/{dir}"):
                    os.makedirs(f"{BACKUP_PATH}/MobileBackup-{current_date}/{dir}")
                with open(f"{BACKUP_PATH}/MobileBackup-{current_date}/{file}", "wb") as f:
                    f.write(data[file])
            except Exception as e:
                logger.error("Error writing file:", e)

        logger.info("Mobile data backed up")

        return True
    return False



def read_file_as_bytes(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
        return data
    except Exception as e:
        logger.error("Error reading file:", e)
        return None



def sync():
    # Checks for all 3 profiles
    for i in range(1,4):
        mobile_profile_exists = True
        mobile_cards_played = -1

        # Mobile
        device = connect_device()
        mobile_profile_bytes: bytes
        output = device.exec_out(f"run-as com.unofficial.balatro cat files/save/game/{i}/profile.jkr", decode=False)

        if isinstance(output, str):
            mobile_profile_bytes = output.encode('utf-8')
        else:
            if output == f"cat: files/save/game/{i}/profile.jkr: No such file or directory\n".encode('utf-8'):
                logger.warning(f"Mobile profile {i} not found.")
                mobile_profile_exists = False
            mobile_profile_bytes = output

        if mobile_profile_exists:
            mobile_profile = zlib.decompress(mobile_profile_bytes, -zlib.MAX_WBITS)
            match = re.search(r'"c_cards_played"]=\s*(\d+)', mobile_profile.decode('utf-8'))

            if match:
                mobile_cards_played = int(match.group(1))
            else:
                logger.warning(f"Cards played not found for mobile profile n°{i}.")

        # PC
        pc_profile_exists = False
        pc_cards_played = -1
        pc_profile_path = f"{SAVE_PATH}/{i}/profile.jkr"

        if os.path.exists(pc_profile_path):
            pc_profile_bytes = read_file_as_bytes(pc_profile_path)
            if pc_profile_bytes:
                pc_profile_exists = True
                pc_profile = zlib.decompress(pc_profile_bytes, -zlib.MAX_WBITS)
                match = re.search(r'"c_cards_played"]=\s*(\d+)', pc_profile.decode('utf-8'))
                if match:
                    pc_cards_played = int(match.group(1))
                else:
                    logger.warning(f"Cards played not found for PC profile n°{i}.")
            else:
                logger.error(f"Failed to read PC profile {i}.")
        else:
            logger.warning(f"PC profile {i} not found.")


        # Compare

        if mobile_profile_exists and mobile_cards_played == -1:
            logger.warning(f"Failed to obtain the cards played for mobile profile n°{i}.")
            continue

        if pc_profile_exists and pc_cards_played == -1:
            logger.warning(f"Failed to obtain the cards played for pc profile n°{i}.")
            continue

        if not mobile_profile_exists and not pc_profile_exists:
            logger.info(f"Profile n°{i} not found on either devices.")
            continue

        logger.info(f"Mobile cards played: {mobile_cards_played}")
        logger.info(f"PC cards played: {pc_cards_played}")

        if pc_cards_played < mobile_cards_played:
            logger.info(f"The mobile data is older for profile n°{i}.")
            if backup_pc():
                transfer_mobile_to_pc(i)
            else:
                logger.error(f"Failed to backup pc data for profile n°{i}.")
        elif pc_cards_played > mobile_cards_played:
            logger.info("The pc data is older.")
            if backup_mobile():
                transfer_pc_to_mobile(i)
            else:
                logger.error("Failed to backup mobile data.")
        else:
            logger.info(f"Both devices have the same data for profile n°{i}.")
    return



def main():
    while True:
        if is_device_online(MOBILE_IP):
            logger.info(f"{MOBILE_IP} is online.")
            sync()
        else:
            logger.info(f"{MOBILE_IP} is offline.")
        time.sleep(300)



if __name__ == "__main__":
    init()
    main()
