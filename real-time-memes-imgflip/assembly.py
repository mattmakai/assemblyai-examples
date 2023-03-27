import asyncio
import base64
import json
import os
import pyaudio
import requests
import webbrowser
import websockets


MEME_TYPES = {'drake':'181913649'}
API_KEY_ASSEMBLYAI = os.getenv('API_KEY_ASSEMBLYAI')
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
if not API_KEY_ASSEMBLYAI:
    print("need to set API_KEY_ASSEMBLYAI as environment variable")
    exit()

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

print(f"Input source: {p.get_default_input_device_info()['name']}\n")

# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"


def only_lower_text(input_text, phrases_to_remove=[]):
    """Removes punctuation from the returned transcription. there's no
       option to do this with real-time transcription YET like it is in
       core transcription, so this is a workaround for now."""
    output_text = input_text.lower().replace(",","").replace(".","")
    for phrase_to_remove in phrases_to_remove:
        output_text = output_text.replace(phrase_to_remove,"").strip()
    output_text = output_text.strip()
    return output_text


async def send_receive():
    # print(f'Connecting websocket to url ${URL}')
    async with websockets.connect(
        URL,
        extra_headers=(("Authorization", API_KEY_ASSEMBLYAI),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:
        await asyncio.sleep(0.1)
        print("Start real-time transcription with Conformer-1...\n")
        session_begins = await _ws.recv()

        print("Say which meme (Drake, SpongeBob, ...), 'top' then what" + \
              " text for the top line, 'bottom' for the bottom line, and" + \
              " 'ship it' to generate the meme.""")
        async def send():
            while True:
                try:
                    data = stream.read(FRAMES_PER_BUFFER,
                                       exception_on_overflow=False)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data":str(data)})
                    await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)
            return True

        async def receive():
            meme_id = ""
            top_text = ""
            bottom_text = ""
            while True:

                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)
                    prompt = result['text']
                    print(prompt, end="\r")
                    if prompt and result['message_type'] == 'FinalTranscript':
                        print("You said '{}'.".format(prompt))
                        if "top" in prompt.lower():
                            top_text = only_lower_text(prompt, ["top"])
                            print("ok, '{}' will be used for the top in the meme.".\
                                  format(top_text))
                        elif "bottom" in prompt.lower():
                            bottom_text = only_lower_text(prompt, ["bottom"])
                            print("ok, '{}' will be used for the bottom text in the meme.".\
                                  format(bottom_text))
                        elif only_lower_text(prompt) in MEME_TYPES.keys():
                            meme_id = MEME_TYPES.get(only_lower_text(prompt))
                            if meme_id:
                                print("ok got the {} meme with template id {}".\
                                      format(only_lower_text(prompt), meme_id))
                            else:
                                print("hmm couldn't find a meme template for that")
                        elif only_lower_text(prompt) == "ship it":
                            print("getting ready to ship with {}, {} and {}".format(top_text,
                                  bottom_text, meme_id))
                            if top_text and bottom_text and meme_id:
                                print("whippin' up that meme!")
                                data = {'template_id': meme_id,
                                        'username': IMGFLIP_USERNAME,
                                        'password': IMGFLIP_PASSWORD,
                                        'text0': top_text, 'text1': bottom_text}
                                resp = requests.post('https://api.imgflip.com/caption_image',
                                                     data=data)
                                meme_url = resp.json()['data']['url']
                                webbrowser.open(meme_url)
                        else:
                            print("say a meme, or 'top', 'bottom', or 'ship it'")
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"

        send_result, receive_result = await asyncio.gather(send(), receive())
        print("receive result:" + receive_result)


if __name__ == "__main__":
    asyncio.run(send_receive())

