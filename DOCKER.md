# Docker

To run this service via docker obviously you need to have installed docker:
- On Windows: install [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
- On Linux: install docker via your package manager (recommended) or via the instructions at https://docs.docker.com/engine/install/

You'll also need to have installed the `adb` command, usually via Android's [`platform-tools`](https://developer.android.com/tools/releases/platform-tools)
- On Windows: you can just download the folder and run the commands by using a terminal in that folder location, usually with the commands in the format `.\adb`
- On Linux: i strongly recommend to install them via your package manager

## Running the service
Once you have docker and adb working you need to:

1) Download the file [`docker-compose.yaml`](docker-compose.yaml) to your computer
2) Edit the values in the following two sections according
  - `volumes`: indicating the folders it will write to
  - `environment`: for setting the device it will connect to and whether to allow backups or not
3) Open a terminal in the file location and run the command `docker compose up --detach`, if everything goes according to plan if should start downloading the image from the registry, you can check if the service is operational with `docker ps`, a successful execution should look like this
  ```bash
    > docker ps

    CONTAINER ID   IMAGE                                                         COMMAND                  CREATED         STATUS         PORTS                                       NAMES
    ebf23212223e   ghcr.io/felipevasquez350/balatro-mobile-adb-autosave:latest   "/app/main"              7 minutes ago   Up 7 minutes                                               balatro-mobile-adb-autosave
  ```

  If you want to check the logs you can do so using the `CONTAINER ID` with the command `docker logs -f ebf23212223e`, the `-f` flag will follow the logs in real time
