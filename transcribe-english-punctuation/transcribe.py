import assemblyai as aai


# the URL of the file we want to transcribe
URL = "https://talkpython.fm/episodes/download/387/build-all-the-things-with-pants-build-system.mp3"

# the file to write the results to, or leave empty to print to console
OUTPUT_FILENAME = "podcast.txt"

# optional configuration settings when you want punctuation, formatting, etc
config = aai.TranscriptionConfig(
  punctuate = True,
  format_text = True,
)

# instantiate the AssemblyAI Python SDK, will use ASSEMBLYAI_API_KEY
# environment variable if it is set, otherwise can be passed in with
# aai.settings.api_key = f"{ASSEMBLYAI_API_KEY}"
transcriber = aai.Transcriber()

# call the API, will block until the API call finishes
transcript = transcriber.transcribe(URL, config)

# write to a file or print to console if no OUTPUT_FILENAME is set
if OUTPUT_FILENAME:
    # save output to a file
    with open(OUTPUT_FILENAME, "w") as file:
        file.write(transcript.text)
else:
    # print to console if no filename
    print(transcript.text)
