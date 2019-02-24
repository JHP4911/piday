import Queue
from array import array
import threading
import sys
import pyaudio
import audioop
import logging
logging.getLogger().setLevel(logging.DEBUG)
 
# Import the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import types
from google.cloud.speech import enums

# first you have to authenticate for the default application: gcloud auth application-default login

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = int(RATE / 10)
SILENCE_THRESHOLD = 500
END_MESSAGE = "Abort!Abort!Abort!"
PAUSE_LENGTH_SECS = 1
PAUSE_LENGTH_IN_SAMPLES = int((PAUSE_LENGTH_SECS * RATE / FRAMES_PER_BUFFER) + 0.5)
 
def print_incoming_speech(responses):
  num_chars_printed = 0
  logging.debug('responses: {}'.format(responses))
  for response in responses:
    if not response.results:
      continue

    result = response.results[0]
    if not result.alternatives:
      continue

    transcript = result.alternatives[0].transcript

    overwrite_chars = ' ' * (num_chars_printed - len(transcript))

    if not result.is_final:
      sys.stdout.write(transcript + overwrite_chars + '\r')
      sys.stdout.flush()
      num_chars_printed = len(transcript)
    else:
      print(transcript + overwrite_chars)

def process_soundbites(sound_filter, sound_source):
  language_code = 'en-US'  # a BCP-47 language tag
  client = speech.SpeechClient()
  config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code=language_code)
  streaming_config = types.StreamingRecognitionConfig(
    config=config,
    interim_results=True)

  requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in sound_filter(sound_source))

  responses = client.streaming_recognize(streaming_config, requests)

  print_incoming_speech(responses)

def main():
  speech_client = speech.SpeechClient()

  audio = pyaudio.PyAudio()
 
  stream = audio.open(format=FORMAT, channels=CHANNELS,
    rate=RATE, input=True,
   frames_per_buffer=FRAMES_PER_BUFFER)

  frames=Queue.Queue()
  speech_processor = threading.Thread(target=process_soundbites, args=(read_microphone, stream,))
  speech_processor.start()

  try:
    while True:
      pass
  except KeyboardInterrupt:
    logging.info('exiting')
    audio.terminate()
    sys.exit()

def read_microphone(stream):
  consecutive_silent_samples = 0
  volume = 0
  while volume <= SILENCE_THRESHOLD:
    data = array('h', stream.read(FRAMES_PER_BUFFER))
    volume = max(data)
  yield data

if __name__ == '__main__':
  main()
