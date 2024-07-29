# Setup

## Android
- Install Balatro via [balatro-mobile-maker](https://github.com/blake502/balatro-mobile-maker)

- Go to `Settings` -> `About Device` -> `Software Information` and click `Build Number` until you unlock `Developer Options`
- Go to `Developer Options` -> `Debugging` -> and enable the following
    - `USB debugging`
    - `Wireless debugging`
    - (not reccomended) you can enable `Disable adb authorisation timeout` to disable the automatic revocation of adb authorization
- Go to your router and obtain your device ip (make it static to avoid it changing in the future)

## PC
- Clone this repository or use the [docker container](DOCKER.md) if you're on Windows
- Install [adb](https://developer.android.com/tools/releases/platform-tools)
- Install [python](https://www.python.org/downloads/)
- (Optional) Create a virtual environment to avoid effecting your system environment
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
- Install the required python packages
    ```bash
    pip install -r requirements.txt
    ```
- Edit the values in the .env.example file (rename it to .env if you don't plan on using docker)
    ```.env
    # Device IP
    MOBILE_IP= # Your device IP, e.g. '192.168.1.2'
    ADB_KEYS_PATH= # Path to store the adb keys, e.g. './adb_keys' to store them in this repo's cloned folder
    SAVE_PATH= # Path to the game save data, on linux it's at '/home/{your_user}/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro'
    ALLOW_BACKUPS= # boolean True or False
    BACKUP_PATH= # Path to store your local backup copies of both versions if ALLOW_BACKUPS is set to True
    ```

- Run the program
    ```bash
    python main.py
    ```
    It will initially get stuck because it cannot connect to the device, here's how to do that

    ### Authorize ADB
    - Ensure you have installed Android platform-tools and have the command `adb` working
    - Connect your device to the pc via USB
    - Enable USB and Wireless Debugging, and allow the connection to the pc, check `Always`
    - On pc, run the following commands:
      ```bash
        adb devices # Check if your device is connected
        adb kill-server # Kill the adb server
        adb tcpip 5555 # restart the adb server at port 5555
        adb connect {your_device_ip} # it should appear another ADB confirmation (for connecting wirelessly to the network), allow that too
        ```
    - You can now remove the cable (USB debugging needs to stay enabled, Wireless can be disabled)

## Systemd
- If you want to run the program in the background as a systemd service, edit the `balatro_autosave.service` file and copy it to `/etc/systemd/system`
    ```bash
        sudo cp balatro_autosave.service /etc/systemd/system/balatro_autosave.service
        sudo systemctl daemon-reload
        sudo systemctl enable balatro_autosave
        sudo systemctl start balatro_autosave

        # To check the status
        sudo systemctl status balatro_autosave
        # or
        journalctl -u balatro_autosave -f
    ```
