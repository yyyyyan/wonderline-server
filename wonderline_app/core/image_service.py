import logging
import os
import uuid
from enum import Enum
from typing import Optional, Dict, Union, List

from minio import ResponseError, Minio
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from wonderline_app.db.minio.base import get_minio_client
from PIL import Image

from wonderline_app.db.minio.exceptions import MinioObjectSavingError

LOGGER = logging.getLogger(__name__)


class ImageTypeNotRecognized(Exception):
    pass


class ImageTypeNotAllowed(Exception):
    pass


class ImageSize(Enum):
    ORIGINAL = 1.0
    LARGE = 0.7
    MEDIUM = 0.5
    SMALL = 0.3
    THUMBNAILS = 0.1


class ImageUploader:
    ALLOWED_FILE_TYPES = ['jpg', 'png']

    def __init__(self, image: FileStorage, minio_client: Minio):
        self.image = image
        self.minio_client = minio_client
        self.image_type = self.get_image_type()

    @property
    def image_filename(self):
        return self.image.filename

    def is_image_type_allowed(self) -> bool:
        return self.image_type in self.ALLOWED_FILE_TYPES

    def get_image_type(self):
        try:
            return secure_filename(self.image_filename).split('.')[-1]
        except Exception:
            raise ImageTypeNotRecognized(f"Failed to recognize the image type for image file: {self.image_filename}")

    def _generate_unique_image_filename(self) -> str:
        return str(uuid.uuid1()) + '.' + self.image_type

    def _save_img_in_tmp_folder_and_return_path(self, image: Union[Image.Image, FileStorage],
                                                image_ratio: ImageSize = ImageSize.ORIGINAL) -> str:
        temporary_image_path = os.path.join(
            os.environ['IMAGE_TMP_FOLDER'],
            image_ratio.name + '_' + self.image_filename)
        image.save(temporary_image_path)
        return temporary_image_path

    @staticmethod
    def _build_minio_url(minio_object_name: str) -> str:
        return "http://localhost" + "/" + os.environ['MINIO_PHOTOS_BUCKET_NAME'] + "/" + minio_object_name

    def _put_image_in_minio_and_return_url(self, image_filepath: str) -> Optional[str]:
        object_name = self._generate_unique_image_filename()
        minio_client = get_minio_client()
        try:
            LOGGER.info(f"Saving the image {image_filepath} into minio with the"
                        f"object name: {object_name} ...")
            minio_client.fput_object(bucket_name='photos', object_name=object_name, file_path=image_filepath)
        except ResponseError as err:
            LOGGER.exception(err)
            raise MinioObjectSavingError(f"Failed to save object {object_name}")
        else:
            return self._build_minio_url(minio_object_name=object_name)

    @staticmethod
    def _remove_tmp_image_file(filepath: str):
        if os.path.exists(filepath):
            os.remove(filepath)
            LOGGER.info(f"Removing the temporary resized file {filepath}")

    def _resize_image(self, original_img_obj: Image.Image, image_size: ImageSize):
        width, height = original_img_obj.width, original_img_obj.height
        resized_width, resized_height = int(image_size.value * width), int(image_size.value * height)
        resized_image = original_img_obj.resize((resized_width, resized_height))
        resized_image_temporary_path = self._save_img_in_tmp_folder_and_return_path(
            image=resized_image,
            image_ratio=image_size)
        resized_image_url = self._put_image_in_minio_and_return_url(image_filepath=resized_image_temporary_path)
        return resized_image_temporary_path, resized_image_url

    def get_image_urls(self, image: FileStorage, resizes: List[ImageSize] = None) -> Dict[str, str]:
        if image is None:
            raise ValueError(f"image is None, expected type: {FileStorage.__name__}")

        if not self.is_image_type_allowed():
            raise ImageTypeNotAllowed(
                f"Image type is not allowed, expect one of {self.ALLOWED_FILE_TYPES}, got {self.image_type}")

        image_size2url = {}

        image_temporary_path = self._save_img_in_tmp_folder_and_return_path(image=image, image_ratio=ImageSize.ORIGINAL)
        original_image_url = self._put_image_in_minio_and_return_url(image_filepath=image_temporary_path)
        LOGGER.debug(f"{ImageSize.ORIGINAL.name} image url: {original_image_url}")
        image_size2url[ImageSize.ORIGINAL.name] = original_image_url
        if resizes is not None:
            im = Image.open(image_temporary_path)
            for image_size in resizes:
                resized_image_temporary_path, resized_image_url = self._resize_image(im, image_size)
                image_size2url[image_size.name] = resized_image_url
                LOGGER.debug(f"{image_size.name} image url: {resized_image_url}")
                self._remove_tmp_image_file(resized_image_temporary_path)
        self._remove_tmp_image_file(image_temporary_path)
        return image_size2url


def upload_image(image: FileStorage) -> Dict[str, str]:
    image_uploader = ImageUploader(image=image, minio_client=get_minio_client())
    return image_uploader.get_image_urls(
        image=image,
        resizes=[ImageSize.SMALL, ImageSize.MEDIUM, ImageSize.THUMBNAILS])
