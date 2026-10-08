from pathlib import Path
import subprocess

from app.services.processors.base import BaseProcessor


class VideoProcessor(BaseProcessor):

    def process(
        self,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:

        operation = operation.lower().strip()

        # ========================================
        # COMPRESS
        # ========================================

        if operation == "compress":
            return self.compress(
                input_path,
                output_path,
                **options,
            )

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
        # EXTRACT AUDIO
        # ========================================

        if operation == "extract_audio":
            return self.extract_audio(
                input_path,
                output_path,
                **options,
            )

        raise ValueError(
            f"Unsupported video operation: {operation}"
        )

    # ========================================
    # COMPRESS
    # ========================================

    def compress(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        quality = int(
            options.get("quality", 70)
        )

        if not 1 <= quality <= 100:
            raise ValueError(
                "Quality must be between 1 and 100"
            )

        # Convert quality into CRF.
        #
        # Lower CRF = better quality / larger file
        # Higher CRF = lower quality / smaller file

        if quality >= 90:
            crf = "18"

        elif quality >= 75:
            crf = "21"

        elif quality >= 50:
            crf = "24"

        elif quality >= 25:
            crf = "28"

        else:
            crf = "32"

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-c:v",
            "libx264",
            "-crf",
            crf,
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_path),
        ]

        self._run_ffmpeg(command)

        return output_path

    # ========================================
    # CONVERT
    # ========================================

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        target_format = options.get("format")

        if not target_format:
            raise ValueError(
                "format is required for video convert"
            )

        target_format = (
            str(target_format)
            .lower()
            .strip()
            .lstrip(".")
        )

        allowed_formats = {
            "mp4",
            "avi",
            "mkv",
            "mov",
            "webm",
        }

        if target_format not in allowed_formats:
            raise ValueError(
                "Unsupported video format. "
                "Use mp4, avi, mkv, mov or webm"
            )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            str(output_path),
        ]

        self._run_ffmpeg(command)

        return output_path

    # ========================================
    # EXTRACT AUDIO
    # ========================================

    def extract_audio(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]

        self._run_ffmpeg(command)

        return output_path

    # ========================================
    # FFMPEG RUNNER
    # ========================================

    @staticmethod
    def _run_ffmpeg(
        command: list[str],
    ) -> None:

        try:

            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:

            raise ValueError(
                "FFmpeg is not installed. "
                "Please install FFmpeg first."
            )

        if result.returncode != 0:

            error_message = (
                result.stderr.strip()
            )

            raise ValueError(
                "FFmpeg processing failed: "
                f"{error_message}"
            )