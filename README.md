# INDIE VOICE TO TEXT TELEGRAM BOT

Based on [OpenAI Whisper](https://github.com/openai/whisper) and [this repo](https://0xacab.org/viperey/telegram-bot-whisper-transcriber/) with slight changes.  

## Requirements

```shell
pip install pydub, python-telegram-bot, openai-whisper
```
It also requires `ffmpeg` to be installed in the system.

## Extra work

You need to create `config.py` file with the following content
```python
TG_TOKEN = 'token from botfather'
my_allowed_chat_ids = '123,1234,12345'
```


## With podman

```shell
podman build -t indie-voice-to-text-bot .
podman run -d localhost/indie-voice-to-text-bot:latest -t indie-voice-to-text-bot
```
create systemd service
```shell
podman generate systemd indie-voice-to-text-bot > ~/.config/systemd/user/indie-voice-to-text-bot.service
systemctl --user enable --now indie-voice-to-text-bot.service
```
