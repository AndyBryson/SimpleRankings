import os
import unittest
from datetime import datetime, timezone
from enum import Enum

from ShipSeatGui.Mongo.mongo_pure_pydantic import MongoPurePydantic
from ShipSeatGui.Mongo.motor import (
    DocumentNotFoundError,
    connect,
    delete_many,
    delete_one,
    find,
    get_from_id,
    insert_many,
    insert_one,
    update_one,
)

from MongoBase import MongoConfigMock, MongoConfigStandard, MongoConfigUrl
from MongoBase.config import SingleInstanceConnection


class EDatabaseTestConnectionType(Enum):
    MOCK = "mock"
    URL = "url"
    STANDARD = "standard"


TEST_LOCAL_MONGO = EDatabaseTestConnectionType.MOCK


class DocumentForTest(MongoPurePydantic):
    __meta__ = {"collection": "document_for_test"}

    name: str
    number: int | None = None


class TestMotor(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        os.environ["MONGODB_USERNAME"] = "test_user"
        match TEST_LOCAL_MONGO:
            case EDatabaseTestConnectionType.MOCK:
                config = MongoConfigMock()
            case EDatabaseTestConnectionType.URL:
                config = MongoConfigUrl(connection_url="mongodb://localhost:27018", database="motor_test")
            case EDatabaseTestConnectionType.STANDARD:
                config = MongoConfigStandard(
                    perform_authentication=False,
                    database="motor_test",
                    connection_info=SingleInstanceConnection(port=27018),
                )
            case _:
                raise NotImplementedError(f"Unknown test connection type {TEST_LOCAL_MONGO}")

        connect(config)

    async def test_save_load_one(self):
        doc1 = DocumentForTest(name="test_save_load_single_1")
        returned_id = await insert_one(doc1)
        assert returned_id == doc1.id

        doc1_returned = await get_from_id(DocumentForTest, returned_id)

        self.assertEqual(doc1_returned, doc1)

    async def test_update_one(self):
        timestamp = round(datetime.now(timezone.utc).timestamp())
        name = f"test_update_one_{timestamp}"
        doc1 = DocumentForTest(name=name, number=1)
        await insert_one(doc1)

        cursor = find(DocumentForTest, name=name, projection=["name", "number"])
        doc1_returned = await cursor.next()

        doc1_returned.number = 2
        await update_one(doc1_returned)

        doc1_updated = await find(DocumentForTest, id=doc1.id).next()

        self.assertEqual(doc1_updated.number, 2)

    async def test_save_load_bulk(self):
        timestamp = round(datetime.now(timezone.utc).timestamp())
        docs = [DocumentForTest(name=f"test_save_load_bulk_{timestamp}_{i}", number=i) for i in range(10)]
        returned_ids = await insert_many(docs)  # type: ignore
        assert len(returned_ids) == len(docs)

        # get all with number less than 5, and name starting with timestamp
        cursor = find(
            DocumentForTest, number__lt=5, query_filter={"name": {"$regex": f"^test_save_load_bulk_{timestamp}"}}
        )

        matched_list = await cursor.to_list(length=100)
        self.assertEqual(5, len(matched_list))

        # test getting all
        cursor = find(DocumentForTest)
        if TEST_LOCAL_MONGO == EDatabaseTestConnectionType.MOCK:
            self.assertEqual(10, len(await cursor.to_list(length=100)))
        else:
            self.assertGreaterEqual(len(await cursor.to_list(length=100)), 10)

    async def test_delete_one(self):
        timestamp = round(datetime.now(timezone.utc).timestamp())
        doc = DocumentForTest(name=f"test_delete_{timestamp}")
        await insert_one(doc)

        doc_returned = await find(DocumentForTest, name=doc.name).next()
        self.assertEqual(doc_returned, doc)

        await delete_one(doc_returned)

        with self.assertRaises(DocumentNotFoundError):
            _doc_deleted = await find(DocumentForTest, name=doc.name).next()

    async def test_delete_many(self):
        timestamp = round(datetime.now(timezone.utc).timestamp())
        docs = [DocumentForTest(name=f"test_save_load_bulk_{timestamp}_{i}", number=i) for i in range(10)]
        returned_ids = await insert_many(docs)  # type: ignore
        assert len(returned_ids) == len(docs)

        # get all with number less than 5, and name starting with timestamp
        await delete_many(
            DocumentForTest, number__lt=5, query_filter={"name": {"$regex": f"^test_save_load_bulk_{timestamp}"}}
        )

        # test getting all
        cursor = find(DocumentForTest, query_filter={"name": {"$regex": f"^test_save_load_bulk_{timestamp}"}})
        self.assertEqual(5, len(await cursor.to_list(length=100)))
