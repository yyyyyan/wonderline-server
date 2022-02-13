import logging
from typing import List, Union, Type, Optional

from cassandra.cqlengine.models import Model

from wonderline_app.api.common.enums import SortType

LOGGER = logging.getLogger(__name__)


# mapping from camel case to snake case
SORTING_MAPPING = {
    SortType.CREATE_TIME.value: 'create_time',
    'liked_nb': 'liked_nb'  # TODO: handle better
}


def convert_sort_by(sort_by: Union[List[str], str]) -> List[str]:
    if isinstance(sort_by, str):
        sort_by = [sort_by]
    converted_sort_by = []
    for s in sort_by:
        has_minus = s.startswith("-")
        s = s.lstrip("-")
        mapped_value = SORTING_MAPPING.get(s, s)
        if has_minus:
            mapped_value = "-" + mapped_value
        converted_sort_by.append(mapped_value)
    return converted_sort_by


def get_filtered_models(
        cls: Type[Model],
        primary_key: str,
        id_value: str,
        sort_by: Optional[Union[str, List[str]]] = 'create_time',
        nb: Optional[int] = 3,
        access_level=None,
        start_index=0
) -> List[Model]:
    models = cls.objects(getattr(cls, primary_key) == id_value)
    if sort_by is not None:
        sort_by: List[str] = convert_sort_by(sort_by)
        models = models.order_by(*sort_by)
    if nb is None:
        models = models.limit(None)
    elif nb < 0:
        raise ValueError(f"nb expected positive or None(no limit), got {nb}")
    else:
        models = models.limit(start_index + nb)

    if access_level is not None:
        models = [model for model in models if model.access_level == access_level]
    if nb is None:
        return models[start_index:]
    else:
        return models[start_index:start_index + nb]
