import os
import subprocess
import base64
from PIL import Image, ImageDraw
import requests
from urllib.parse import urlparse


class VideoGenerator:

    def __init__(self, image_path=None, reel=True):
        """
        Initialize with optional image path and reel flag.
        Reel mode uses 9:16 aspect ratio (608x1080).
        """
        self.reel = reel
        self.video_resolution = (608, 1080) if reel else None
        self.image_path = self.process_image(image_path)
        if not self.image_path:  # Ensure we always have a valid path
            self.image_path = self.create_blank_image("/tmp/blank_image.png")

    def process_image(self, image_path):
        """Process the input image based on its source and validity"""
        if not image_path or not isinstance(image_path,
                                            (str, bytes, os.PathLike)):
            return None

        # Handle base64 image
        if isinstance(image_path, str) and image_path.startswith("data:image"):
            return self.process_base64_image(
                image_path) if self.is_valid_base64(image_path) else None

        # Handle web URL
        if isinstance(image_path, str) and image_path.startswith("http"):
            return self.download_image(image_path)

        # Handle local file
        if isinstance(image_path, str) and os.path.exists(
                str(image_path)):  # Convert to str to ensure valid input
            return self.prepare_local_image(image_path)

        return None

    def is_valid_base64(self, image_path):
        """Check if base64 string is valid"""
        try:
            header, base64_data = image_path.split(",", 1)
            base64.b64decode(base64_data)
            return True
        except Exception:
            return False

    def process_base64_image(self, image_path):
        """Process valid base64 image"""
        try:
            header, base64_data = image_path.split(",", 1)
            image_data = base64.b64decode(base64_data)
            temp_path = "/tmp/base64_image.png"
            with open(temp_path, "wb") as img_file:
                img_file.write(image_data)
            return self.prepare_local_image(temp_path)
        except Exception:
            return None

    def prepare_local_image(self, image_path):
        """Place local image on appropriate canvas"""
        try:
            image = Image.open(image_path)
            if self.reel:
                return self.embed_image_on_canvas(image, "/tmp/reel_image.png",
                                                  (608, 1080))
            return image_path
        except Exception:
            return None

    def embed_image_on_canvas(self, image, output_path, resolution):
        """Embed image onto a canvas with specified resolution"""
        try:
            canvas = Image.new("RGB", resolution, (0, 0, 0))
            image.thumbnail(resolution, Image.Resampling.LANCZOS)
            x_offset = (resolution[0] - image.width) // 2
            y_offset = (resolution[1] - image.height) // 2
            canvas.paste(image, (x_offset, y_offset))
            canvas.save(output_path)
            return output_path
        except Exception:
            return None

    def download_image(self, image_url):
        """Download image from web and place on canvas"""
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            filename = os.path.basename(
                urlparse(image_url).path) or "downloaded_image.png"
            local_path = os.path.join("/tmp", filename)

            with open(local_path, 'wb') as img_file:
                for chunk in response.iter_content(chunk_size=8192):
                    img_file.write(chunk)

            image = Image.open(local_path)
            if self.reel:
                return self.embed_image_on_canvas(image, local_path,
                                                  (608, 1080))
            return local_path
        except Exception:
            return None

    def create_blank_image(self, output_path):
        """Create a blank image with appropriate resolution"""
        resolution = (608, 1080) if self.reel else (1920, 1080)
        image = Image.new("RGB", resolution, (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((resolution[0] // 3, resolution[1] // 2),
                  "Blank Frame",
                  fill="white")
        image.save(output_path)
        return output_path

    def generate(self, audio_path: str):
        """Generate video with the processed image and audio"""
        if not isinstance(audio_path, str) or not os.path.exists(audio_path):
            print("Invalid or missing audio file")
            return None

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_video = f"{base_name}_reel.mp4" if self.reel else f"{base_name}_video.mp4"
        output_video = os.path.join("/tmp", output_video)

        # Ensure we have a valid image path
        if not isinstance(self.image_path, str) or not os.path.exists(
                self.image_path):
            self.image_path = self.create_blank_image("/tmp/blank_image.png")

        resolution = (608,
                      1080) if self.reel else Image.open(self.image_path).size
        command = [
            "ffmpeg", "-loop", "1", "-i", self.image_path, "-i", audio_path,
            "-vf", f"scale={resolution[0]}:{resolution[1]}", "-c:v", "libx264",
            "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-pix_fmt",
            "yuv420p", "-shortest", output_video
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Video generated: {output_video}")
            return output_video
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate video: {e}")
            return None
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Deleted audio file: {audio_path}")
            if os.path.exists(self.image_path):
                os.remove(self.image_path)
                print(f"Deleted image file: {self.image_path}")
