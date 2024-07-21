# Setup

## Android
- Install Balatro via [balatro-mobile-maker](https://github.com/blake502/balatro-mobile-maker)

- Go to `Settings` -> `About Device` -> `Software Information` and click `Build Number` until you unlock `Developer Options`
- Go to `Developer Options` -> `Debugging` -> and enable the following
    - `USB debugging`
    - `Wireless debugging`
    - (not reccomended) you can enable `Disable adb authorisation timeout` to disable the automatic revocation of adb authorization
- Go to your router and obtain your device ip (make it static)

## PC
- Clone this repository
- Install [adb](https://developer.android.com/studio/command-line/adb)
- Install [python](https://www.python.org/downloads/)
- (Optional) Create a virtual environment
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
- Install the required python packages
    ```bash
    pip install -r requirements.txt
    ```
- Edit the values at the top of `main.py` to match your device
    ```python
    # Device IP
    DEVICE_IP = # Your device IP, e.g. '192.168.1.2'
    TMP_PATH= # Temporary path to store the files, e.g. '/absolute/path/to/tmp'
    ADB_KEYS_PATH= # Path to store the adb keys, e.g. '/absolute/path/to/adb_keys'
    GAME_PATH= # Path to the game, usually on linux '/home/{your_user}/.local/share/Steam/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro'
    ```

- Run the program
    ```bash
    python main.py
    ```
    It will initially get stuck because it cannot connect to the device, here's how to

    ### Authorize ADB
    - Connect device to PC via USB
    - Enable USB Debugging and allow the connection to the pc, check `Always`
    - On pc, run the program, it should appear another ADB confirmation (for connecting wirelessly this time), allow that too
    - You can now remove the cable (but USB debugging needs to stay enabled)


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


