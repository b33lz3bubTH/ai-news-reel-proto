import subprocess
import uuid
import os

class PiperTextToSpeech:
    def __init__(self, piper_binary_path: str = os.path.expanduser("~/.piper/piper/piper"), model: str = "en_US-ryan-high.onnx"):
        self.piper_binary_path = piper_binary_path
        # Assume model is in the same directory as piper unless a full path is provided
        self.model_path = model if os.path.isabs(model) else os.path.join(os.path.dirname(piper_binary_path), model)

    def generate(self, text: str) -> str:
        """
        Generate an audio file from the given text using the Piper binary.
        """
        output_filename = f"/tmp/{uuid.uuid4()}.wav"

        command = [
            self.piper_binary_path,
            "--model",
            self.model_path,
            "--output_file",
            output_filename,
        ]
        try:
            # Pipe the text into the subprocess
            subprocess.run(command, input=text.encode(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Audio generated: {output_filename}")
            return output_filename
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr.decode('utf-8')}")
            raise
