# from pathlib import Path

# from PIL import Image

# from app.services.processors.base import BaseProcessor


# class ImageProcessor(BaseProcessor):

#     def process(
#         self,
#         input_path: Path,
#         output_path: Path,
#         **options,
#     ) -> Path:

#         operation = options.get("operation")

#         if operation == "convert":
#             return self.convert(
#                 input_path,
#                 output_path,
#             )

#         if operation == "compress":
#             return self.compress(
#                 input_path,
#                 output_path,
#                 options,
#             )

#         if operation == "resize":
#             return self.resize(
#                 input_path,
#                 output_path,
#                 options,
#             )

#         raise ValueError(
#             f"Unsupported image operation: {operation}"
#         )

#     def convert(
#         self,
#         input_path: Path,
#         output_path: Path,
#     ) -> Path:

#         image = Image.open(input_path)

#         image.save(output_path)

#         image.close()

#         return output_path

#     def compress(
#         self,
#         input_path: Path,
#         output_path: Path,
#         options: dict,
#     ) -> Path:

#         image = Image.open(input_path)

#         quality = options.get("quality", 70)

#         image.save(
#             output_path,
#             quality=quality,
#             optimize=True,
#         )

#         image.close()

#         return output_path

#     def resize(
#         self,
#         input_path: Path,
#         output_path: Path,
#         options: dict,
#     ) -> Path:

#         image = Image.open(input_path)

#         width = options.get("width")
#         height = options.get("height")

#         if not width or not height:
#             raise ValueError(
#                 "Width and height are required for resize"
#             )

#         resized_image = image.resize(
#             (width, height)
#         )

#         resized_image.save(output_path)

#         image.close()
#         resized_image.close()

#         return output_path

# 2nd try



# from pathlib import Path

# from PIL import Image

# from app.services.processors.base import BaseProcessor


# class ImageProcessor(BaseProcessor):

#     def process(
#         self,
#         input_path: Path,
#         output_path: Path,
#         **options,
#     ) -> Path:

#         image = Image.open(input_path)

#         operation = options.get("operation")

#         if operation == "convert":
#             image.save(output_path)

#         elif operation == "compress":
#             quality = options.get("quality", 70)

#             image.save(
#                 output_path,
#                 quality=quality,
#                 optimize=True,
#             )

#         elif operation == "resize":
#             width = options.get("width")
#             height = options.get("height")

#             if not width or not height:
#                 raise ValueError(
#                     "Width and height are required for resize"
#                 )

#             resized_image = image.resize(
#                 (width, height)
#             )

#             resized_image.save(output_path)

#         else:
#             raise ValueError(
#                 f"Unsupported image operation: {operation}"
#             )

#         return output_path
    
    
    
    #  3rd try
    
    
# from pathlib import Path

# from PIL import Image

# from app.services.processors.base import BaseProcessor


# class ImageProcessor(BaseProcessor):

#     def process(
#         self,
#         input_path: Path,
#         output_path: Path,
#         **options,
#     ) -> Path:

#         image = Image.open(input_path)

#         operation = options.get("operation")

#         if operation == "convert":

#             image.save(
#                 output_path
#             )

#         elif operation == "compress":

#             quality = options.get(
#                 "quality",
#                 70,
#             )

#             image.save(
#                 output_path,
#                 quality=quality,
#                 optimize=True,
#             )

#         elif operation == "resize":

#             width = options.get("width")
#             height = options.get("height")

#             if not width or not height:
#                 raise ValueError(
#                     "Width and height are required for resize"
#                 )

#             resized_image = image.resize(
#                 (width, height)
#             )

#             resized_image.save(
#                 output_path
#             )

#         else:

#             raise ValueError(
#                 f"Unsupported image operation: {operation}"
#             )

#         return output_path


#   ithink its last and final
from pathlib import Path

from PIL import Image

from app.services.processors.base import BaseProcessor


class ImageProcessor(BaseProcessor):

    def process(
        self,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:

        operation = operation.lower().strip()

        if operation == "compress":
            return self.compress(
                input_path,
                output_path,
                **options,
            )

        if operation == "convert":
            return self.convert(
                input_path,
                output_path,
                **options,
            )

        if operation == "resize":
            return self.resize(
                input_path,
                output_path,
                **options,
            )

        if operation == "crop":
            return self.crop(
                input_path,
                output_path,
                **options,
            )

        raise ValueError(
            f"Unsupported image operation: {operation}"
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

        quality = options.get("quality", 80)

        try:
            quality = int(quality)
        except (TypeError, ValueError):
            raise ValueError(
                "Quality must be an integer"
            )

        if not 1 <= quality <= 100:
            raise ValueError(
                "Quality must be between 1 and 100"
            )

        image = Image.open(input_path)

        image_format = image.format

        if not image_format:
            raise ValueError(
                "Unable to determine image format"
            )

        image_format = image_format.upper()

        # --------------------------------
        # JPEG
        # --------------------------------

        if image_format == "JPEG":

            image = image.convert("RGB")

            image.save(
                output_path,
                format="JPEG",
                quality=quality,
                optimize=True,
            )

        # --------------------------------
        # WEBP
        # --------------------------------

        elif image_format == "WEBP":

            image.save(
                output_path,
                format="WEBP",
                quality=quality,
                method=6,
            )

        # --------------------------------
        # PNG
        # --------------------------------

        elif image_format == "PNG":

            image.save(
                output_path,
                format="PNG",
                optimize=True,
                compress_level=9,
            )

        # --------------------------------
        # Other formats
        # --------------------------------

        else:

            image.save(
                output_path,
                format=image_format,
            )

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

        image = Image.open(input_path)

        target_format = options.get("format")

        if not target_format:
            raise ValueError(
                "format is required for convert"
            )

        target_format = (
            str(target_format)
            .lower()
            .strip()
            .lstrip(".")
        )

        format_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "webp": "WEBP",
            "bmp": "BMP",
            "gif": "GIF",
        }

        pil_format = format_map.get(
            target_format
        )

        if not pil_format:
            raise ValueError(
                f"Unsupported image format: {target_format}"
            )

        # JPEG does not support RGBA
        if pil_format == "JPEG":

            if image.mode not in (
                "RGB",
                "L",
            ):
                image = image.convert("RGB")

        image.save(
            output_path,
            format=pil_format,
        )

        return output_path

    # ========================================
    # RESIZE
    # ========================================

    def resize(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        width = options.get("width")
        height = options.get("height")

        if width is None or height is None:
            raise ValueError(
                "width and height are required for resize"
            )

        try:
            width = int(width)
            height = int(height)

        except (TypeError, ValueError):
            raise ValueError(
                "width and height must be integers"
            )

        if width <= 0 or height <= 0:
            raise ValueError(
                "width and height must be positive"
            )

        image = Image.open(input_path)

        resized = image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

        image_format = image.format

        if not image_format:
            raise ValueError(
                "Unable to determine image format"
            )

        # JPEG needs RGB
        if image_format.upper() == "JPEG":
            resized = resized.convert("RGB")

        resized.save(
            output_path,
            format=image_format,
        )

        return output_path

    # ========================================
    # CROP
    # ========================================

    def crop(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        left = options.get("left")
        top = options.get("top")
        right = options.get("right")
        bottom = options.get("bottom")

        # --------------------------------
        # Check required values
        # --------------------------------

        if (
            left is None
            or top is None
            or right is None
            or bottom is None
        ):
            raise ValueError(
                "left, top, right and bottom "
                "are required for crop"
            )

        # --------------------------------
        # Convert to integers
        # --------------------------------

        try:

            left = int(left)
            top = int(top)
            right = int(right)
            bottom = int(bottom)

        except (TypeError, ValueError):

            raise ValueError(
                "Crop coordinates must be integers"
            )

        # --------------------------------
        # Open image
        # --------------------------------

        image = Image.open(input_path)

        # --------------------------------
        # Validate coordinates
        # --------------------------------

        if left < 0:
            raise ValueError(
                "left cannot be negative"
            )

        if top < 0:
            raise ValueError(
                "top cannot be negative"
            )

        if right <= left:
            raise ValueError(
                "right must be greater than left"
            )

        if bottom <= top:
            raise ValueError(
                "bottom must be greater than top"
            )

        if right > image.width:
            raise ValueError(
                "right exceeds image width"
            )

        if bottom > image.height:
            raise ValueError(
                "bottom exceeds image height"
            )

        # --------------------------------
        # Crop
        # --------------------------------

        cropped = image.crop(
            (
                left,
                top,
                right,
                bottom,
            )
        )

        image_format = image.format

        if not image_format:
            raise ValueError(
                "Unable to determine image format"
            )

        # JPEG needs RGB
        if image_format.upper() == "JPEG":
            cropped = cropped.convert("RGB")

        cropped.save(
            output_path,
            format=image_format,
        )

        return output_path