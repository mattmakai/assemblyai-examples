import pyaudio
import websocket
import base64
import json
import time
import threading
import os

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

p = pyaudio.PyAudio()

# starts recording
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"


def print_text(wsapp, message):
    if message and 'text' in message:
        result = json.loads(message)
        prompt = result['text']
        print(prompt, end="\r")
        if result['message_type'] == 'FinalTranscript':
            print("{}".format(prompt))


def send_mic_data(ws):
    print(f"Input source: {p.get_default_input_device_info()['name']}\n")
    def run():
        while True:
            try:
                data = stream.read(FRAMES_PER_BUFFER,
                                   exception_on_overflow=False)
                data64 = base64.b64encode(data).decode("utf-8")
                json_data = json.dumps({"audio_data":str(data64)})
                ws.send(json_data)
            except Exception as e:
                print(e)
                exit()
            time.sleep(0.1)
    threading.Thread(target=run).start()


#wsapp = websocket.WebSocketApp("wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000",
#                               on_message=print_text, header={"Authorization":os.getenv("API_KEY_ASSEMBLYAI")})
#wsapp.on_open = send_mic_data
#wsapp.run_forever()

