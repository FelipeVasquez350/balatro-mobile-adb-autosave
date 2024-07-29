FROM python:3.9-slim AS builder

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y gcc musl-dev libffi-dev libssl-dev python3-dev build-essential
RUN pip install -r requirements.txt
RUN pyinstaller --onefile main.py


FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libstdc++6 && \
    apt-get clean

ENV ADB_KEYS_PATH=/adbkeys
ENV SAVE_PATH=/Balatro
ENV BACKUP_PATH=/BalatroBackups

COPY --from=builder /app/dist/main /app/main

RUN chmod +x /app/main

CMD ["/app/main"]
