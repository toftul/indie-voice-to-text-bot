# INDIE VOICE TO TEXT TELEGRAM BOT

Based on [OpenAI Whisper](https://github.com/openai/whisper) and [this repo](https://0xacab.org/viperey/telegram-bot-whisper-transcriber/) with slight changes.  

## Requirements

```shell
pip install pydub, python-telegram-bot, openai-whisper
```

## Extra work

You need to create `config.py` file with the following content
```python
TG_TOKEN = 'token from botfather'
my_allowed_chat_ids = '123,1234,12345'
```
