FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository universe
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    python3.10 \
    python3-pip

WORKDIR /opt/indie-voice-to-text-bot
COPY requirements.txt .

RUN pip3.10 install -r requirements.txt

COPY *.py .
RUN ls -lsa
RUN pwd

CMD ["python3.10", "bot.py"]

