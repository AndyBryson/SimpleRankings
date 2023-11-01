from typing import Any, Generic, Type, TypeVar

from bson import ObjectId
from loguru import logger
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from MongoBase import MongoConfig, MongoConfigMock, MongoConfigStandard, MongoConfigUrl

from .mongo_pure_pydantic import MongoPurePydantic

T = TypeVar("T", bound=MongoPurePydantic)

__all__ = [
    "insert_one",
    "update_one",
    "save",
    "get_from_id",
    "connect",
    "find",
    "insert_many",
    "delete_one",
    "delete_many",
    "DocumentNotFoundError",
]

__connection: AsyncIOMotorClient | None = None
__database: AsyncIOMotorDatabase | None = None


class DocumentNotFoundError(Exception):
    pass


class PydanticAsyncIOMotorCursor(Generic[T]):
    """
    Wrapper for Override the motor cursor to return pydantic documents
    """

    def __init__(self, cursor, type: Type[MongoPurePydantic]):
        self.cursor = cursor
        self.__type = type

    async def __aiter__(self):
        async for doc in self.cursor:
            pydantic_doc = self.__type(**doc)
            yield pydantic_doc

    def sort(self, *args, **kwargs):
        self.cursor.sort(*args, **kwargs)
        return self

    def where(self, *args, **kwargs):
        self.cursor.where(*args, **kwargs)
        return self

    def each(self, callback):
        def new_callback(doc):
            return callback(self.__type(**doc))

        self.cursor.each(new_callback)
        return self

    def skip(self, skip: int):
        self.cursor.skip(skip)
        return self

    def rewind(self):
        self.cursor.rewind()
        return self

    def limit(self, limit: int):
        self.cursor.limit(limit)
        return self

    def _dict_to_pydantic(self, d: dict[str, Any]) -> T:
        return self.__type(**d)  # type: ignore

    async def next(self) -> T:
        try:
            d = await self.cursor.next()
        except StopAsyncIteration:
            raise DocumentNotFoundError("No more documents in cursor") from None

        return self._dict_to_pydantic(d)

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)

    async def to_list(self, length: int | None = None):
        return [self._dict_to_pydantic(doc) for doc in await self.cursor.to_list(length=length)]


def connect(config: MongoConfig, **kwargs) -> AsyncIOMotorClient:  # pyright: ignore[reportGeneralTypeIssues]
    match config:
        case MongoConfigStandard():
            if config.start_read_only:
                if "username" not in kwargs:
                    kwargs["username"] = config.read_only_username
                if "password" not in kwargs:
                    kwargs["password"] = config.read_only_password

            kwargs = config.get_connection_kwargs(**kwargs)

            # these kwargs are in pymongo but not motor. I guess we'll fully remove them one day.
            banned_kwargs = ["alias", "db"]

            for banned_kwarg in banned_kwargs:
                kwargs.pop(banned_kwarg, None)

            replacement_kwargs = {
                "authentication_source": "authSource",
            }
            for key, value in replacement_kwargs.items():
                if key in kwargs:
                    kwargs[value] = kwargs.pop(key)

            ret = AsyncIOMotorClient(**kwargs)
            _set_connection_and_database(ret, config.database)
            return ret

        case MongoConfigUrl():
            kwargs = {**config.connection_kwargs, **kwargs}
            if config.username and "username" not in kwargs:
                kwargs["username"] = config.username

            if config.password and "password" not in kwargs:
                kwargs["password"] = config.password

            if config.database and "db" not in kwargs:
                kwargs["db"] = config.database

            ret = AsyncIOMotorClient(host=config.connection_url, UuidRepresentation="standard", **kwargs)
            _set_connection_and_database(ret, kwargs["db"])
            return ret

        case MongoConfigMock():
            ret = AsyncMongoMockClient(tz_aware=True)
            _set_connection_and_database(ret, config.database)
            return ret
        case _:
            raise NotImplementedError(f"Unknown mongo config type {config.type}")


def _set_connection_and_database(connection, database):
    global __database
    global __connection
    __connection = connection
    __database = connection[database]


def _get_collection(doc: MongoPurePydantic | T):
    assert __connection is not None and __database is not None, "Must call set_connection_and_database"
    return __database[doc.__meta__["collection"]]  # type: ignore


async def insert_one(doc: MongoPurePydantic, *, user: str = "") -> ObjectId:
    collection = _get_collection(doc)

    doc.apply_metadata(user=user)
    d = doc.to_mongo(exclude_none=True)
    try:
        result = await collection.insert_one(d)
    except Exception as ex:
        logger.error("Document insert failed. {} : {}", ex, d)
        raise

    if result.inserted_id is None:
        raise ValueError("Document insert failed")

    doc.id = result.inserted_id
    return doc.id


async def update_one(doc: MongoPurePydantic, *, user: str = ""):
    collection = _get_collection(doc)
    doc.apply_metadata(user=user, add_created=False)

    update_dict = doc.to_mongo(exclude_none=True, exclude_unset=True)

    try:
        await collection.update_one({"_id": doc.id}, {"$set": update_dict})
    except Exception:
        logger.error("Document update failed. {} : {}", doc.id, update_dict)
        raise


async def save(doc: MongoPurePydantic, *, user: str = ""):
    if doc.id is None or doc.date_created is None:
        await insert_one(doc, user=user)
    else:
        await update_one(doc, user=user)


async def insert_many(docs: list[MongoPurePydantic], *, user: str = "") -> list[ObjectId]:
    assert all(type(doc) == type(docs[0]) for doc in docs), "All docs must be of the same type"  # noqa: E721

    collection = _get_collection(docs[0])

    for doc in docs:
        doc.apply_metadata(user=user)

    try:
        result = await collection.insert_many([doc.to_mongo(exclude_none=True) for doc in docs])
    except Exception:
        logger.exception("Document insert failed")
        raise
    return result.inserted_ids


def find(
    doc_type: Type[T],
    query_filter: dict[str, dict[str, Any]] | None = None,
    projection: list[str] | dict[str, Any] | None = None,
    find_kwargs: dict[str, Any] | None = None,
    **kwargs,
) -> PydanticAsyncIOMotorCursor[T]:
    collection = _get_collection(doc_type)

    query_filter = query_filter if query_filter else {}
    projection = projection if projection else []
    find_kwargs = find_kwargs if find_kwargs else {}

    for key, value in kwargs.items():
        if "__" in key:
            key, test = key.split("__")
            query_filter[key] = {f"${test}": value}
        else:
            query_filter[key] = {"$eq": value}

    key_aliases = {field.name: field.alias for field in doc_type.__fields__.values() if field.alias}

    query_filter = {key_aliases.get(key, key): value for key, value in query_filter.items()}
    if isinstance(projection, list):
        projection = {key_aliases.get(key, key): 1 for key in projection}
    else:
        projection = {key_aliases.get(key, key): value for key, value in projection.items()}

    if projection and "_id" not in projection:
        projection["_id"] = 1

    cursor = collection.find(filter=query_filter, projection=projection, **find_kwargs)

    ret = PydanticAsyncIOMotorCursor(cursor=cursor, type=doc_type)
    return ret


async def get_from_id(doc_type: Type[T], id: str | ObjectId) -> T:
    collection = _get_collection(doc_type)
    try:
        returned_dict = await collection.find_one({"_id": id})
    except Exception:
        logger.exception("Document get failed")
        raise
    if not returned_dict:
        raise ValueError(f"Could not find {doc_type} with id {id}")
    return doc_type(**returned_dict)


async def delete_one(doc: MongoPurePydantic):
    collection = _get_collection(doc)

    try:
        await collection.delete_one({"_id": doc.id})
    except Exception:
        logger.exception("Document delete failed")
        raise


async def delete_many(doc_type: Type[T], query_filter: dict[str, dict[str, Any]] | None = None, **kwargs):
    collection = _get_collection(doc_type)

    query_filter = query_filter if query_filter else {}

    for key, value in kwargs.items():
        if "__" in key:
            key, test = key.split("__")
            query_filter[key] = {f"${test}": value}
        else:
            query_filter[key] = {"$eq": value}

    key_aliases = {field.name: field.alias for field in doc_type.__fields__.values() if field.alias}

    query_filter = {key_aliases.get(key, key): value for key, value in query_filter.items()}

    try:
        await collection.delete_many(query_filter)
    except Exception:
        logger.exception("Document delete failed")
        raise
