# from pathlib import Path
# import subprocess

# from app.services.processors.base import BaseProcessor


# class AudioProcessor(BaseProcessor):

#     def process(
#         self,
#         input_path: Path,
#         output_path: Path,
#         operation: str,
#         **options,
#     ) -> Path:

#         operation = operation.lower().strip()

#         # ========================================
#         # COMPRESS
#         # ========================================

#         if operation == "compress":
#             return self.compress(
#                 input_path,
#                 output_path,
#                 **options,
#             )

#         # ========================================
#         # CONVERT
#         # ========================================

#         if operation == "convert":
#             return self.convert(
#                 input_path,
#                 output_path,
#                 **options,
#             )

#         raise ValueError(
#             f"Unsupported audio operation: {operation}"
#         )

#     # ========================================
#     # COMPRESS
#     # ========================================

#     def compress(
#         self,
#         input_path: Path,
#         output_path: Path,
#         **options,
#     ) -> Path:

#         quality = int(
#             options.get("quality", 70)
#         )

#         if not 1 <= quality <= 100:
#             raise ValueError(
#                 "Quality must be between 1 and 100"
#             )

#         # Convert quality 1-100
#         # into MP3 bitrate.
#         #
#         # Higher quality = higher bitrate.

#         if quality >= 90:
#             bitrate = "320k"

#         elif quality >= 75:
#             bitrate = "256k"

#         elif quality >= 50:
#             bitrate = "192k"

#         elif quality >= 25:
#             bitrate = "128k"

#         else:
#             bitrate = "96k"

#         self._run_ffmpeg(
#             input_path=input_path,
#             output_path=output_path,
#             bitrate=bitrate,
#         )

#         return output_path

#     # ========================================
#     # CONVERT
#     # ========================================

#     def convert(
#         self,
#         input_path: Path,
#         output_path: Path,
#         **options,
#     ) -> Path:

#         target_format = options.get("format")

#         if not target_format:
#             raise ValueError(
#                 "format is required for audio convert"
#             )

#         target_format = (
#             str(target_format)
#             .lower()
#             .strip()
#             .lstrip(".")
#         )

#         allowed_formats = {
#             "mp3",
#             "wav",
#             "ogg",
#             "aac",
#             "flac",
#             "m4a",
#         }

#         if target_format not in allowed_formats:
#             raise ValueError(
#                 "Unsupported audio format. "
#                 "Use mp3, wav, ogg, aac, flac or m4a"
#             )

#         self._run_ffmpeg(
#             input_path=input_path,
#             output_path=output_path,
#         )

#         return output_path

#     # ========================================
#     # FFMPEG
#     # ========================================

#     @staticmethod
#     def _run_ffmpeg(
#         input_path: Path,
#         output_path: Path,
#         bitrate: str | None = None,
#     ) -> None:

#         command = [
#             "ffmpeg",
#             "-y",
#             "-i",
#             str(input_path),
#         ]

#         # If bitrate is supplied,
#         # we are compressing audio.

#         if bitrate:

#             command.extend(
#                 [
#                     "-b:a",
#                     bitrate,
#                 ]
#             )

#         command.append(
#             str(output_path)
#         )

#         try:

#             result = subprocess.run(
#                 command,
#                 check=False,
#                 capture_output=True,
#                 text=True,
#             )

#         except FileNotFoundError:

#             raise ValueError(
#                 "FFmpeg is not installed. "
#                 "Please install FFmpeg first."
#             )

#         if result.returncode != 0:

#             error_message = (
#                 result.stderr.strip()
#             )

#             raise ValueError(
#                 "FFmpeg processing failed: "
#                 f"{error_message}"
#             )
from pathlib import Path
import subprocess

from app.services.processors.base import BaseProcessor


class AudioProcessor(BaseProcessor):

    def process(
        self,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:

        operation = operation.lower().strip()

        # ========================================
        # CONVERT
        # ========================================

        if operation == "convert":
            return self.convert(
                input_path,
                output_path,
                **options,
            )

        # ========================================
        # COMPRESS
        # ========================================

        if operation == "compress":
            return self.compress(
                input_path,
                output_path,
                **options,
            )

        raise ValueError(
            f"Unsupported audio operation: {operation}"
        )

    # ========================================
    # CONVERT AUDIO
    # ========================================

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        audio_format = options.get("format")

        if not audio_format:
            raise ValueError(
                "format is required for audio convert"
            )

        audio_format = (
            str(audio_format)
            .lower()
            .strip()
            .lstrip(".")
        )

        allowed_formats = {
            "mp3",
            "wav",
            "ogg",
            "aac",
            "flac",
            "m4a",
        }

        if audio_format not in allowed_formats:
            raise ValueError(
                "Unsupported audio format. "
                "Use mp3, wav, ogg, aac, flac or m4a"
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(input_path),
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:

            raise ValueError(
                "FFmpeg is not installed"
            )

        except subprocess.CalledProcessError as exc:

            raise ValueError(
                f"Audio conversion failed: {exc.stderr}"
            )

        if not output_path.exists():

            raise ValueError(
                "Converted audio file was not created"
            )

        return output_path

    # ========================================
    # COMPRESS AUDIO
    # ========================================

    def compress(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        bitrate = options.get(
            "bitrate",
            "128k",
        )

        bitrate = (
            str(bitrate)
            .lower()
            .strip()
        )

        allowed_bitrates = {
            "64k",
            "96k",
            "128k",
            "160k",
            "192k",
            "256k",
            "320k",
        }

        if bitrate not in allowed_bitrates:
            raise ValueError(
                "Unsupported bitrate. "
                "Use 64k, 96k, 128k, 160k, "
                "192k, 256k or 320k"
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(input_path),
                    "-b:a",
                    bitrate,
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:

            raise ValueError(
                "FFmpeg is not installed"
            )

        except subprocess.CalledProcessError as exc:

            raise ValueError(
                f"Audio compression failed: {exc.stderr}"
            )

        if not output_path.exists():

            raise ValueError(
                "Compressed audio file was not created"
            )

        return output_path