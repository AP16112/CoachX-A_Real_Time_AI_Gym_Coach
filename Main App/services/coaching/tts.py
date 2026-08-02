# IN this file, we will write the logic for converting text to speech using the gTTS (Google Text-to-Speech) library. The gTTS library allows us to convert text into spoken audio, which can be useful for providing auditory feedback or instructions in our application.


from io import BytesIO    # We are importing BytesIO from the io module to create an in-memory binary stream. This allows us to handle audio data without needing to write it to a physical file, making the process more efficient and suitable for real-time applications.
# SO this BytesIO object will act as a file-like buffer that we can write the generated speech audio to, and then read from it when we need to play the audio or send it over a network.

# We are importing the gTTS class from the gtts module. The gTTS (Google Text-to-Speech) library is a Python interface to Google's Text-to-Speech API, which allows us to convert text into spoken audio in various languages. We will use this class to generate speech from text input in our application.
from gtts import gTTS


class TextToSpeech:
    # This method takes a text string and an optional language code (defaulting to English) as input. It uses the gTTS library to convert the text into speech, writes the audio data to an in-memory buffer, and returns the audio data as bytes. If the input text is empty or None, it simply returns without generating any audio.
    def speak(self, text, lang="en"):
        # Here we are cleaning the input text by stripping any leading or trailing whitespace. If the text is None, we default to an empty string to avoid errors. This ensures that we only process valid, non-empty text for speech generation.
        cleaned = (text or "").strip()

        if not cleaned:
            return
        
        # We create a BytesIO buffer to hold the generated audio data. This allows us to work with the audio in memory without needing to save it to a physical file, which is useful for real-time applications where we want to play or transmit the audio immediately.
        buffer = BytesIO()

        # Now we use the gTTS library to convert the cleaned text into speech. We specify the language using the lang parameter (defaulting to English). The write_to_fp method writes the generated audio data directly to our in-memory buffer, allowing us to capture the audio without creating a temporary file.
        gTTS(text=cleaned, lang=lang).write_to_fp(buffer)

        # After writing the audio data to the buffer, we reset the buffer's position to the beginning using seek(0). This is important because after writing, the buffer's position is at the end, and we need to read from the start when we return the audio data.
        buffer.seek(0)

        # Finally, we read the audio data from the buffer and return it as bytes. This allows the caller to access the generated speech audio directly, which can then be played or transmitted as needed.
        return buffer.read()
    
