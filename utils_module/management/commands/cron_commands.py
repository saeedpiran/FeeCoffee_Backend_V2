# my_app/management/commands/cron_commands.py

import io
import os
from datetime import timedelta

from PIL import Image, ImageOps
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts_module.models import UserMediaFiles
from article_module.models import ArticleMediaFiles
from product_module.models import ProductMediaFiles
from shop_module.models import ShopMediaFiles
from site_module.models import SiteSetting


# class Command(BaseCommand):
#     help = "Clean up expired outstanding tokens (older than 30 days) and blacklisted tokens (older than 10 days)."
#
#     def handle(self, *args, **options):
#         # Clean up outstanding tokens that expired more than 30 days ago.
#         outstanding_deleted = cleanup_old_outstanding_tokens(days=45)
#
#         # Clean up blacklisted tokens that were created more than 10 days ago.
#         blacklisted_deleted = cleanup_old_blacklisted_tokens(days=10)
#
#         # Output the result
#         self.stdout.write(
#             self.style.SUCCESS(
#                 f"Deleted {outstanding_deleted} outstanding tokens and {blacklisted_deleted} blacklisted tokens."
#             )
#         )


class Command(BaseCommand):
    help = (
        "Deletes auth tokens older than the configured period and "
        "Optimize images by resizing the larger side to 800px (if necessary) and reducing quality until the file size is below 100KB."
    )

    # These parameters can be adjusted to your liking.
    RESIZE_LIMIT = 800  # Maximum pixel size for the larger dimension.
    TARGET_SIZE_KB = 100  # Desired maximum file size (in kilobytes) after compression.
    INITIAL_QUALITY = 85  # Start quality for compression.
    MIN_QUALITY = 20  # Do not lower quality past this value.
    QUALITY_STEP = 5  # Quality decrement in each iteration.

    def handle(self, *args, **kwargs):
        # -----------------------------------------------------------------------------------
        # --- Part 1: Delete Old Tokens ---
        site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
        token_validity_days = site_setting.old_token_deletion if site_setting else 15
        threshold_date = timezone.now() - timedelta(days=token_validity_days)
        deleted_count, _ = Token.objects.filter(created__lt=threshold_date).delete()
        self.stdout.write(f"Deleted {deleted_count} tokens older than {token_validity_days} days.")

        # -----------------------------------------------------------------------------------
        # --- Part 2: Optimize Images and Convert to WebP ---
        models_to_process = [
            (UserMediaFiles, "UserMediaFiles"),
            (ArticleMediaFiles, "ArticleMediaFiles"),
            (ProductMediaFiles, "ProductMediaFiles"),
            (ShopMediaFiles, "ShopMediaFiles"),
        ]

        total_optimized_images = 0
        total_resized_images = 0

        for model_class, model_name in models_to_process:
            self.stdout.write(f"Processing {model_name}...")
            qs = model_class.objects.filter(file__isnull=False, optimized=False)
            model_optimized_count = 0
            model_resized_count = 0

            for instance in qs:
                file_path = instance.file.path

                if not os.path.exists(file_path):
                    self.stderr.write(f"File not found: {file_path}")
                    continue

                try:
                    with Image.open(file_path) as img:
                        try:
                            # Correct orientation based on EXIF data.
                            img = ImageOps.exif_transpose(img)
                        except Exception:
                            pass

                        # Convert RGBA images to RGB for JPEG compatibility.
                        if img.mode == "RGBA":
                            img = img.convert("RGB")

                        # Select the proper resampling filter.
                        resample_filter = getattr(Image, "Resampling", Image).LANCZOS

                        # Get current dimensions.
                        width, height = img.size

                        # --------------------------------------------------------------------
                        # Custom resizing for ShopMediaFiles.
                        if model_name == "ShopMediaFiles":
                            if instance.media_type == ShopMediaFiles.BANNERIMAGE:
                                # For banner images, target size = 1200 x 400.
                                target_width = 1200
                                target_height = 400
                                if width > target_width or height > target_height:
                                    ratio = min(target_width / float(width), target_height / float(height))
                                    new_size = (int(width * ratio), int(height * ratio))
                                    img = img.resize(new_size, resample_filter)
                                    model_resized_count += 1
                                    self.stdout.write(f"Resized shop banner image to {new_size} for {file_path}.")
                            elif instance.media_type == ShopMediaFiles.CERTIFICATE:
                                # For certificates, which are vertical and intended for high-quality print,
                                # define a higher resolution plus less aggressive compression.
                                target_width = 1200
                                target_height = 1600
                                if width > target_width or height > target_height:
                                    ratio = min(target_width / float(width), target_height / float(height))
                                    new_size = (int(width * ratio), int(height * ratio))
                                    img = img.resize(new_size, resample_filter)
                                    model_resized_count += 1
                                    self.stdout.write(f"Resized certificate image to {new_size} for {file_path}.")
                            else:
                                # Default resizing for other shop media files.
                                if max(width, height) > self.RESIZE_LIMIT:
                                    ratio = self.RESIZE_LIMIT / float(max(width, height))
                                    new_size = (int(width * ratio), int(height * ratio))
                                    img = img.resize(new_size, resample_filter)
                                    model_resized_count += 1
                                    self.stdout.write(f"Resized shop image to {new_size} for {file_path}.")
                        else:
                            # Default resizing logic for non-shop media files.
                            if max(width, height) > self.RESIZE_LIMIT:
                                ratio = self.RESIZE_LIMIT / float(max(width, height))
                                new_size = (int(width * ratio), int(height * ratio))
                                img = img.resize(new_size, resample_filter)
                                model_resized_count += 1
                                self.stdout.write(f"Resized image to {new_size} for {file_path}.")

                        # Determine image format; default to JPEG for compression purposes.
                        img_format = img.format if img.format else "JPEG"

                        # --------------------------------------------------------------------
                        # Step 2: Iteratively reduce quality to meet target file size.
                        # For certificates, we use certificate-specific compression settings.
                        if model_name == "ShopMediaFiles" and instance.media_type == ShopMediaFiles.CERTIFICATE:
                            target_bytes = 300 * 1024  # Certificate images: target ~300 KB.
                            quality = 95  # Start with a high quality (to preserve details for print).
                            min_quality = 85  # Do not compress certificate images below 85.
                        else:
                            target_bytes = self.TARGET_SIZE_KB * 1024
                            quality = self.INITIAL_QUALITY
                            min_quality = self.MIN_QUALITY

                        final_buffer = None
                        size = 0  # Initialize to avoid reference errors.
                        while quality >= min_quality:
                            buffer = io.BytesIO()
                            try:
                                img.save(buffer, format=img_format, optimize=True, quality=quality)
                            except IOError as e:
                                self.stderr.write(f"IOError saving {file_path} at quality {quality}: {e}")
                                break

                            size = buffer.tell()
                            if size <= target_bytes:
                                self.stdout.write(
                                    f"Achieved target size {size / 1024:.1f}KB at quality {quality} for {file_path}"
                                )
                                final_buffer = buffer
                                break

                            quality -= self.QUALITY_STEP

                        # In case target size wasn't reached, use the last generated buffer.
                        if final_buffer is None:
                            final_buffer = buffer
                            self.stdout.write(
                                f"Used minimum quality with size {size / 1024:.1f}KB for {file_path}"
                            )

                    # Write the optimized image back to the file.
                    with open(file_path, "wb") as f:
                        f.write(final_buffer.getvalue())

                    # Mark the instance as optimized.
                    instance.optimized = True
                    instance.save()
                    model_optimized_count += 1
                    self.stdout.write(f"Optimized image: {file_path}")

                except Exception as e:
                    self.stderr.write(f"Error processing {file_path}: {e}")

            # Log summary per model.
            self.stdout.write(
                f"Finished processing {model_name}: Optimized {model_optimized_count} images with {model_resized_count} images resized."
            )
            total_optimized_images += model_optimized_count
            total_resized_images += model_resized_count

            self.stdout.write(f"Finished processing {model_name}.")

        # Log overall summary.
        self.stdout.write(
            f"Image optimization complete: Total optimized images: {total_optimized_images}, Total images resized: {total_resized_images}."
        )
        self.stdout.write("Image optimization complete for new media files.")

        # -----------------------------------------------------------------------------------
