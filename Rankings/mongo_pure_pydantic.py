import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel, Field

__all__ = ["MongoPurePydantic", "ensure_timezone_aware", "datetime_encoder"]


def ensure_timezone_aware(dt: datetime) -> datetime:
    """
    Make a datetime timezone aware. If it is already timezone aware, then we just return it.
    """
    if not dt.tzinfo or not dt.tzinfo.utcoffset(dt):
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def datetime_encoder(dt: datetime | None) -> str | None:
    """
    Encode an optional datetime for a mongodb document. If the datetime is None, then we return None.
    """
    if not dt:
        return dt
    return ensure_timezone_aware(dt).isoformat()


#: The fields that are common to all mongo documents that are in the DB. When sending them in Pydantic, we normally
#: remove them
DATABASE_FIELDS = {"id", "date_created", "date_modified", "created_by", "modified_by", "deleted"}


class MongoPurePydantic(BaseModel):
    """
    A pydantic model that can live in our mongo database
    """

    __meta__: dict[str, Any] = {}

    def __init_subclass__(cls, **kwargs):
        """
        Method to ensure that the subclass has the correct meta information
        """
        super().__init_subclass__(**kwargs)

        parent_defaults = getattr(cls, "__meta__", {})
        if "abstract" not in cls.__meta__:
            cls.__meta__["abstract"] = False

        cls.__meta__ = {**parent_defaults, **cls.__meta__}

        if not cls.__meta__.get("abstract", False):
            if not cls.__meta__.get("collection", None):
                raise ValueError("MongoPurePydantic subclasses must define a collection name if they are not abstract")

    id: ObjectId | None = Field(
        default=None,
        alias="_id",
        description="The unique ID of the document, should be an ObjectId, but can be overridden.",
    )
    date_created: datetime | None = Field(
        default=None, alias="_date_created", description="The date that the document was created"
    )
    date_modified: datetime | None = Field(
        default=None, alias="_date_modified", description="The date that the document was last modified"
    )
    created_by: str | None = Field(default=None, alias="_created_by", description="The user that created the document")
    modified_by: str | None = Field(
        default=None, alias="_modified_by", description="The user that last modified the document"
    )
    deleted: bool | None = Field(
        default=False, alias="_deleted", description="Whether the document has been deleted -- used by MongoAtlas"
    )

    @staticmethod
    def item_to_mongo(item: Any) -> Any:
        """
        Convert an item to something that can be stored in mongo.
        """
        match item:
            case Enum():
                return item.value
            case UUID():
                return str(item)
            case dict():
                return MongoPurePydantic.dict_to_mongo(item)
            case list():
                return [MongoPurePydantic.item_to_mongo(i) for i in item]
            case _:
                return item

    @staticmethod
    def dict_to_mongo(d: dict[str, Any]) -> dict[str, Any]:
        """
        Convert a dictionary to a dictionary that can be stored in mongo.
        """
        for key, value in d.items():
            d[key] = MongoPurePydantic.item_to_mongo(value)

        return d

    def to_mongo(self, **pydantic_dict_args) -> dict[str, Any]:
        """
        Convert the pydantic model to a dictionary that can be stored in mongo.
        """
        d = self.dict(exclude_database_fields=False, by_alias=True, **pydantic_dict_args)
        d = self.dict_to_mongo(d)
        return d

    def json(self, exclude_database_fields: bool = True, *args, **kwargs):
        """
        Convert the pydantic model to a json string that can be stored in mongo.

        :param exclude_database_fields: Whether to exclude the database fields from the json string. Useful for sending
                                        with fastapi
        """
        if exclude_database_fields:
            if "exclude" in kwargs:
                kwargs["exclude"].update(DATABASE_FIELDS - self.required_fields)
            else:
                kwargs["exclude"] = DATABASE_FIELDS - self.required_fields
        return super().json(*args, **kwargs)

    def dict(self, exclude_database_fields: bool = True, *args, **kwargs):
        """
        Override the pydantic dict method to exclude the database fields by default.
        """
        if exclude_database_fields:
            if "exclude" in kwargs and kwargs["exclude"]:
                kwargs["exclude"] = set(kwargs["exclude"]) | (DATABASE_FIELDS - self.required_fields)
            else:
                kwargs["exclude"] = DATABASE_FIELDS - self.required_fields
        return super().dict(*args, **kwargs)

    @property
    def required_fields(self) -> set[str]:
        """
        Get the fields that are required for this model
        """
        return {name for name, field_info in self.__fields__.items() if field_info.required}

    class Config:
        json_encoders = {datetime: datetime_encoder, ObjectId: str, Enum: lambda x: x.value}
        underscore_attrs_are_private = False
        arbitrary_types_allowed = True

    def apply_metadata(self, *, user: str = "", add_created: bool = True):
        """
        Apply the metadata to the document. This will set the date_modified and modified_by fields. If the document
        has not been created yet, then it will set the date_created and created_by fields as well.
        """
        if not user:
            user = os.getenv("MONGODB_USERNAME", "")

        if add_created and self.date_created is None:
            self.date_created = datetime.now(timezone.utc)
            self.created_by = user

        self.date_modified = datetime.now(timezone.utc)
        self.modified_by = user
