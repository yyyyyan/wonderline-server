import base64
import datetime
import logging
import os
import uuid
from enum import Enum
from typing import Dict, Union, List

from werkzeug.utils import secure_filename
from PIL import Image

from wonderline_app.db.minio.base import put_object_in_minio_and_return_url, object_exists_in_minio, \
    remove_object_from_minio

LOGGER = logging.getLogger(__name__)
DEFAULT_AVATAR_URL = "http://localhost/photos/default_avatar.png"


class ImageTypeNotRecognized(Exception):
    pass


class ImageTypeNotAllowed(Exception):
    pass


class ImageSize(Enum):
    ORIGINAL = (1.0, 1.0)
    LARGE = (0.7, 0.7)
    MEDIUM = (0.5, 0.5)
    SMALL = (0.3, 0.3)
    THUMBNAILS = (0.1, 0.1)
    AVATAR = (180, 180)


class ImageStorage:
    def __init__(self, img_str):
        self.img_str = img_str
        self.filename = self.get_filename_by_timestamp()

    @staticmethod
    def get_filename_by_timestamp() -> str:
        return str(int(datetime.datetime.now().replace(microsecond=0).timestamp())) + '.png'

    def save(self, filepath):
        with open(filepath, "wb") as fh:
            fh.write(base64.decodebytes(self.img_str.encode()))


class ImageUploader:
    ALLOWED_FILE_TYPES = ['jpg', 'png']

    def __init__(self, image: ImageStorage, bucket_name: str):
        self.image = image
        self.minio_bucket_name = bucket_name
        self.image_type = self._get_image_type()

    @property
    def image_filename(self):
        return self.image.filename

    def is_image_type_allowed(self) -> bool:
        return self.image_type in self.ALLOWED_FILE_TYPES

    def _get_image_type(self) -> str:
        """Get image type from image filename"""
        try:
            return secure_filename(self.image_filename).split('.')[-1]
        except Exception:
            raise ImageTypeNotRecognized(f"Failed to recognize the image type for image file: {self.image_filename}")

    def _generate_unique_image_filename(self) -> str:
        return str(uuid.uuid1()) + '.' + self.image_type

    def _save_img_in_tmp_folder_and_return_path(self, image: Union[Image.Image, ImageStorage],
                                                image_ratio: ImageSize = ImageSize.ORIGINAL) -> str:
        """Save the image in a temporary folder and return the saving path"""
        temporary_image_path = os.path.join(
            os.environ['IMAGE_TMP_FOLDER'],
            image_ratio.name + '_' + self.image_filename)
        image.save(temporary_image_path)
        return temporary_image_path

    def _build_minio_url(self, minio_object_name: str) -> str:
        """Get the URL of image in Minio for download"""
        return "http://localhost" + "/" + self.minio_bucket_name + "/" + minio_object_name

    @staticmethod
    def _remove_tmp_image_file(filepath: str):
        """Remove the image in the temporary folder if possible"""
        if os.path.exists(filepath):
            os.remove(filepath)
            LOGGER.info(f"Removing the temporary resized file {filepath}")

    def _resize_image(self, original_img_obj: Image.Image, image_size: ImageSize):
        """Resize original image"""
        width, height = original_img_obj.width, original_img_obj.height
        w, h = image_size.value[0], image_size.value[1]
        if isinstance(w, float):
            new_width_size = int(w * width)
        else:
            new_width_size = w
        if isinstance(h, float):
            new_height_size = int(h * height)
        else:
            new_height_size = h
        resized_width, resized_height = int(new_width_size), int(new_height_size)
        resized_image = original_img_obj.resize((resized_width, resized_height))
        resized_image_temporary_path = self._save_img_in_tmp_folder_and_return_path(
            image=resized_image,
            image_ratio=image_size)
        resized_image_url = put_object_in_minio_and_return_url(
            bucket_name=self.minio_bucket_name,
            object_name=self._generate_unique_image_filename(),
            file_path=resized_image_temporary_path,
        )
        return resized_image_temporary_path, resized_image_url

    def get_image_urls(self, image: ImageStorage, sizes: List[ImageSize]) -> Dict[str, str]:
        """Get the mapping from image size to image URL"""
        if image is None:
            raise ValueError(f"image is None, expected type: {ImageStorage.__name__}")

        if not self.is_image_type_allowed():
            raise ImageTypeNotAllowed(
                f"Image type is not allowed, expect one of {self.ALLOWED_FILE_TYPES}, got {self.image_type}")
        image_size2url = {}
        image_temporary_path = self._save_img_in_tmp_folder_and_return_path(image=image, image_ratio=ImageSize.ORIGINAL)

        if ImageSize.ORIGINAL in sizes:
            original_image_url = put_object_in_minio_and_return_url(
                bucket_name=self.minio_bucket_name,
                object_name=self._generate_unique_image_filename(),
                file_path=image_temporary_path,
            )
            LOGGER.info(f"{ImageSize.ORIGINAL.name} image url: {original_image_url}")
            image_size2url[ImageSize.ORIGINAL.name] = original_image_url
            sizes.remove(ImageSize.ORIGINAL)
        im = Image.open(image_temporary_path)
        for image_size in sizes:
            resized_image_temporary_path, resized_image_url = self._resize_image(im, image_size)
            image_size2url[image_size.name] = resized_image_url
            LOGGER.info(f"{image_size.name} image url: {resized_image_url}")
            self._remove_tmp_image_file(resized_image_temporary_path)
        self._remove_tmp_image_file(image_temporary_path)
        return image_size2url


def upload_encoded_image(image: str, sizes: List[ImageSize] = None,
                         bucket_name: str = os.environ['MINIO_PHOTOS_BUCKET_NAME']) -> Dict[str, str]:
    """Upload the encoded image (by base64) to Minio and return generated URL mapping for different size(s)"""
    if sizes is None:
        sizes = [ImageSize.ORIGINAL]
    image = ImageStorage(image)
    image_uploader = ImageUploader(
        image=image,
        bucket_name=bucket_name)
    return image_uploader.get_image_urls(image=image, sizes=sizes)


def upload_default_avatar_if_possible():
    photo_bucket = os.environ['MINIO_PHOTOS_BUCKET_NAME']
    default_avatar_path = os.environ['DEFAULT_AVATAR_PATH']
    object_name = default_avatar_path.split('/')[-1]
    if not object_exists_in_minio(
            bucket_name=photo_bucket,
            object_name=object_name):
        put_object_in_minio_and_return_url(
            bucket_name=photo_bucket,
            file_path=default_avatar_path,
            object_name=object_name
        )


def remove_image_by_url(url: str):
    photos_bucket_name = os.environ['MINIO_PHOTOS_BUCKET_NAME']
    object_name = url.split(photos_bucket_name)[1]
    remove_object_from_minio(bucket_name=photos_bucket_name, object_name=object_name)
