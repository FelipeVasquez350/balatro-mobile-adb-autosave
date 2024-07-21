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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Balatro Sync started.")

load_dotenv()
MOBILE_IP=
TMP_PATH=
ADB_KEYS_PATH=
GAME_PATH=
MOBILE_TMP_PATH= "/data/local/tmp/balatro"

def __init__():
    success = False
    if MOBILE_IP == None:
        logger.info("Please set the MOBILE_IP environment variable")
        return
    logger.info("Initializing")
    while not success:
        if is_device_online(MOBILE_IP):
            try:
                if connect_device():
                    success = True
                else:
                    logger.info("Error connecting to device. Retrying...")
            except Exception as e:
                logger.info(f"Error: {e}")
        else:
            logger.info("Device not online. Retrying in 5 seconds")
            time.sleep
    logger.info("Initialization complete")


def is_device_online(ip):
    try:
        host = ping(ip, count=5,  timeout=1, privileged=False)
    except NameLookupError:
        return False
    return host.packets_sent == host.packets_received



def connect_device():
    if not os.path.exists(ADB_KEYS_PATH):
        os.makedirs(ADB_KEYS_PATH)
        logger.info("Generating a public/private key pair")
        keygen(f"{ADB_KEYS_PATH}/adbkey")

    with open(f"{ADB_KEYS_PATH}/adbkey") as f:
        priv = f.read()
    with open(f"{ADB_KEYS_PATH}/adbkey" + '.pub') as f:
        pub = f.read()
    signer = PythonRSASigner(pub, priv)

    device = AdbDeviceTcp(MOBILE_IP, 5555, default_transport_timeout_s=9.0)
    device.connect(rsa_keys=[signer], auth_timeout_s=10)

    logger.info("Connected to the device")
    return device


def transfer_pc_to_mobile(device):
    local_user = os.popen("whoami").read().strip()

    device.shell(f"mkdir {MOBILE_TMP_PATH}")
    device.shell(f"mkdir {MOBILE_TMP_PATH}/files")
    device.shell(f"mkdir {MOBILE_TMP_PATH}/files/save")
    device.shell(f"mkdir {MOBILE_TMP_PATH}/files/save/game")

    logger.info("Transferring PC data to mobile")
    files = os.listdir(GAME_PATH)

    def push_files(device, dir):
        for file in os.listdir(dir):
            if os.path.isdir(f"{dir}/{file}"):
                push_files(device, f"{dir}/{file}")
            elif file != "steam_autocloud.vdf":
                path = dir.replace(GAME_PATH,"")
                device.push(f"{dir}/{file}", f"{MOBILE_TMP_PATH}/files/save/game/{path}/{file}")


    push_files(device, GAME_PATH)

    device.shell("am force-stop com.unofficial.balatro")
    device.shell(f"run-as com.unofficial.balatro cp -r {MOBILE_TMP_PATH}/files .")
    device.shell(f"rm -r {MOBILE_TMP_PATH}")

    logger.info("PC data transferred to mobile")
    return


def transfer_mobile_to_pc(device):
    device.shell(f"rm -r {MOBILE_TMP_PATH}")
    device.shell(f"mkdir {MOBILE_TMP_PATH}")
    device.shell(f"mkdir {MOBILE_TMP_PATH}/files")
    device.shell(f"mkdir {MOBILE_TMP_PATH}/files/1")

    device.shell(f"run-as com.unofficial.balatro cat files/save/game/settings.jkr > {MOBILE_TMP_PATH}/files/settings.jkr")
    device.shell(f"touch {MOBILE_TMP_PATH}/files/1/profile.jkr")
    device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/profile.jkr > {MOBILE_TMP_PATH}/files/1/profile.jkr")
    device.shell(f"touch {MOBILE_TMP_PATH}/files/1/meta.jkr")
    device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/meta.jkr > {MOBILE_TMP_PATH}/files/1/meta.jkr")
    device.shell(f"touch {MOBILE_TMP_PATH}/files/1/save.jkr")
    device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/save.jkr > {MOBILE_TMP_PATH}/files/1/save.jkr")
    device.shell(f"find {MOBILE_TMP_PATH}/files/ -maxdepth 2 -size 0c -exec rm '{"{}"}' \\;")

    local_user = os.popen("whoami").read().strip()

    def pull_files(device, dir):
        list = device.list(dir)
        for file in list:
            if file.filename.decode('utf-8') != "." and file.filename.decode('utf-8') != "..":
                logger.info(f"Pulling {dir}{file.filename.decode('utf-8')}")
                is_dir = device.shell(f"[ -d {dir}{file.filename.decode('utf-8')} ] && echo 1 || echo 0")
                if is_dir == "1\n":
                    logger.info(f"{file.filename.decode('utf-8')} is a directory")
                    pull_files(device, f"{dir}{file.filename.decode('utf-8')}/")
                else:
                    path = dir.replace(f"{MOBILE_TMP_PATH}/files/","")

                    if not os.path.exists(f"{GAME_PATH}/{path}"):
                        os.makedirs(f"{GAME_PATH}/{path}")
                    device.pull(f"{dir}{file.filename.decode('utf-8')}", f"{GAME_PATH}/{path}{file.filename.decode('utf-8')}")

    if os.path.exists(f"{GAME_PATH}"):
        pull_files(device, f"{MOBILE_TMP_PATH}/files/")
        logger.info("Mobile data transferred to PC")
        device.shell(f"rm -r {MOBILE_TMP_PATH}")
        return True

    device.shell(f"rm -r {MOBILE_TMP_PATH}")
    logger.info("Mobile data DID NOT transfer to PC")

    return False


def backup_pc():
    local_user = os.popen("whoami").read().strip()
    if os.path.exists(GAME_PATH):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.mkdir(f"{GAME_PATH}Backup-{current_date}")

        os.system(f"cp -r {GAME_PATH} {GAME_PATH}Backup-{current_date}/")

        logger.info("PC data backed up")
        return True
    return False


def backup_mobile():
    device = connect_device()
    local_user = os.popen("whoami").read().strip()

    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if os.path.exists(GAME_PATH):
        os.mkdir(f"{GAME_PATH}MobileBackup-{current_date}")

        device.shell(f"rm -r {MOBILE_TMP_PATH}")
        device.shell(f"mkdir {MOBILE_TMP_PATH}")
        device.shell(f"mkdir {MOBILE_TMP_PATH}/files")
        device.shell(f"mkdir {MOBILE_TMP_PATH}/files/1/")

        device.shell(f"run-as com.unofficial.balatro cat files/save/game/settings.jkr > {MOBILE_TMP_PATH}/files/settings.jkr")
        device.shell(f"touch {MOBILE_TMP_PATH}/files/1/profile.jkr")
        device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/profile.jkr > {MOBILE_TMP_PATH}/files/1/profile.jkr")
        device.shell(f"touch {MOBILE_TMP_PATH}/files/1/meta.jkr")
        device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/meta.jkr > {MOBILE_TMP_PATH}/files/1/meta.jkr")
        device.shell(f"touch {MOBILE_TMP_PATH}/files/1/save.jkr")
        device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/save.jkr > {MOBILE_TMP_PATH}/files/1/save.jkr")
        device.shell(f"find {MOBILE_TMP_PATH}/files/ -maxdepth 2 -size 0c -exec rm '{"{}"}' \\;")

        def pull_files(device, dir):
            list = device.list(dir)
            for file in list:
                if file.filename.decode('utf-8') != "." and file.filename.decode('utf-8') != "..":
                    logger.info(f"Pulling {dir}{file.filename.decode('utf-8')}")
                    is_dir = device.shell(f"[ -d {dir}{file.filename.decode('utf-8')} ] && echo 1 || echo 0")
                    if is_dir == "1\n":
                        logger.info(f"{file.filename.decode('utf-8')} is a directory")
                        pull_files(device, f"{dir}{file.filename.decode('utf-8')}/")
                    else:
                        path = dir.replace(f"{MOBILE_TMP_PATH}/files/","")

                        if not os.path.exists(f"{GAME_PATH}MobileBackup-{current_date}/{path}"):
                            os.makedirs(f"{GAME_PATH}MobileBackup-{current_date}/{path}")
                        device.pull(f"{dir}{file.filename.decode('utf-8')}", f"{GAME_PATH}MobileBackup-{current_date}/{path}{file.filename.decode('utf-8')}")

        pull_files(device, f"{MOBILE_TMP_PATH}/files/")

        device.shell(f"rm -r {MOBILE_TMP_PATH}")

        logger.info("Mobile data backed up")

        return True
    return False


def read_file_as_bytes(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
        return data
    except Exception as e:
        logger.info("Error reading file:", e)
        return None


def decompress_data_deflate(data):
    try:
        decompressed_data = zlib.decompress(data, -zlib.MAX_WBITS)
        return decompressed_data
    except Exception as e:
        logger.info("Error decompressing deflate data:", e)
        return None


def obtain_cards_played(file_path):
    file_data = read_file_as_bytes(file_path)

    if file_data:
        decompressed_data = decompress_data_deflate(file_data)

        if decompressed_data:
            pattern = r'"c_cards_played"]=\s*(\d+)'

            match = re.search(pattern, decompressed_data.decode('utf-8'))

            if match:
                cards_played = int(match.group(1))
                return cards_played
            else:
                logger.info("Key not found.")
                return None

        else:
            logger.info("Failed to decompress data.")
            return None
    else:
        logger.info("Failed to read file.")
        return None


def sync():
    local_user = os.popen("whoami").read().strip()
    pc_profile_path = f"{GAME_PATH}/1/profile.jkr"

    device = connect_device()
    device.shell(f"mkdir {MOBILE_TMP_PATH}")
    device.shell(f"run-as com.unofficial.balatro cat files/save/game/1/profile.jkr > {MOBILE_TMP_PATH}/profile.jkr")

    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    device.pull(f"{MOBILE_TMP_PATH}/profile.jkr", f"{TMP_PATH}/profile.jkr")
    device.shell(f"rm -r {MOBILE_TMP_PATH}")

    mobile_profile_path = f"{TMP_PATH}/profile.jkr"
    pc_profile_path = f"{GAME_PATH}/1/profile.jkr"

    mobile_cards_played = obtain_cards_played(mobile_profile_path)
    pc_cards_played = obtain_cards_played(pc_profile_path)

    os.remove(mobile_profile_path)

    logger.info(f"Mobile cards played: {mobile_cards_played}")
    logger.info(f"PC cards played: {pc_cards_played}")

    if mobile_cards_played == None or pc_cards_played == None:
        logger.info("Failed to obtain the cards played.")
        return

    if pc_cards_played < mobile_cards_played:
        logger.info("The mobile data is older.")
        if backup_pc():
            transfer_mobile_to_pc(connect_device())
        else:
            logger.info("Failed to backup pc data.")
    elif pc_cards_played > mobile_cards_played:
        logger.info("The pc data is older.")
        if backup_mobile():
            transfer_pc_to_mobile(connect_device())
        else:
            logger.info("Failed to backup mobile data.")
    else:
        logger.info("Both devices have the same data. (in terms of the cards played)")
    return


def main():
    while True:
        if is_device_online(MOBILE_IP):
            logger.info(f"{MOBILE_IP} is online.")
            sync()
        else:
            logger.info(f"{MOBILE_IP} is offline.")
        time.sleep(60)


if __name__ == "__main__":
    __init__()
    main()
