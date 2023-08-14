# pip install assemblyai>=0.15.1
import assemblyai as aai

URL = "https://talkpython.fm/episodes/download/410/the-intersection-of-tabular-data-and-generative-ai.mp3"
transcript = aai.Transcriber().transcribe(URL)

params = {"context":"This is a Python programming podcast interview.",
          "answer_format":"Five bullet points, one sentence each bullet."}
result = transcript.lemur.summarize(**params)
print("Summarized in five bullet points:")
print(result.response)

params['answer_format'] = "One long sentence."
result = transcript.lemur.summarize(**params)
print("Summarized in one long sentence:")
print(result.response)

params['answer_format'] = "Short summary description no longer than 20 words."
result = transcript.lemur.summarize(**params)
print("Summarized in a description no longer than 20 words:")
print(result.response)
