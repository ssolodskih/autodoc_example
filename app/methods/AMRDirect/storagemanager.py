import asyncio
import datetime
import json
import logging
import os
import random
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from beanie import Document, init_beanie
from motor import motor_asyncio
from pydantic_factories import ModelFactory, BeanieDocumentFactory

from abstracts import StorageManager, IntermediateData

export_keys = {
    'visualizer_bytes'
}  # TODO define export keys so image bytes are excluded

include_keys = {
    'id': True,
    'model': {
        'birthday_day': True,
        'birthday_month': True,
        'birthday_year': True,
        'gender_id': True
    },
    'data': {'__all__': {
        'id_': True,
        'measure_time': True,
        'id_result_argument': True,
        'result': True
    }}
}


class LoggingStorageManager(StorageManager):
    def __init__(self, conn_config: dict):
        self.conn_config = conn_config
        logging.basicConfig(level=logging.DEBUG, filename=self.conn_config['filename'],
                            format='%(asctime)s::%(levelname)s::%(message)s')

    def store(self, data_to_store: IntermediateData) -> bool:
        logging.debug(data_to_store.json())
        return True


class JsonStorageManager(StorageManager):
    def __init__(self, conn_config: dict):
        self.conn_config = conn_config
        self._jsonfile = Path(self.conn_config['filename'])
        self.sane_history = None
        self._init_storage()

    def _init_storage(self):
        if not self._jsonfile.exists():
            self._jsonfile.write_text('[]')
        else:
            self._check_sanity()

    def _check_sanity(self):
        """
        If the json file is corrupted, rename it and create a new one
        """
        try:
            with open(self._jsonfile) as f:
                self.sane_history = json.load(f)
        except JSONDecodeError:
            old_json_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            rand_number = random.randint(100000, 999999)
            self._jsonfile.rename(f'{old_json_datetime}_log_{rand_number}.json')
            self._jsonfile.write_text('[]')

    def _read_history(self) -> list:
        """
        It reads the history file and returns a list of the history items
        :return: A list of dictionaries.
        """
        if self.sane_history is None:
            with open(self._jsonfile) as f:
                return json.load(f)
        else:
            return self.sane_history

    def store(self, data_to_store: IntermediateData) -> bool:
        """
        Reads the history from the file, appends the new data to the history, and writes the history back to the file

        :param data_to_store: The data to store
        :type data_to_store: IntermediateData
        :return: A boolean value.
        """
        history = self._read_history()

        payload = {'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   'payload': data_to_store.json()}
        history.append(payload)
        with open(self._jsonfile, 'w') as f:
            json.dump(history, f, ensure_ascii=False, indent=3)
        return True


class AMRData(IntermediateData, Document):
    """Helper class for proper stringification of the JSON fields needed for MongoDB."""
    timestamp: datetime = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            int: lambda v: str(v)
        }


class MongoStorageManager(StorageManager):
    def __init__(self, conn_config: dict):
        self.conn_config = conn_config
        self.collection = None
        self.client = None
        self.connected = False

    @staticmethod
    def _create_conn_string() -> str | None:
        """
        If the environment variables `MONGO_USERNAME` and `MONGO_PASSWORD` are set, then return a connection string with
        those values, otherwise return `None`
        :return: A string that is the connection string to the mongo database.
        """
        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        host = 'mongo' if os.getenv('DOCKERIZED', False) else 'localhost'
        if username and password:
            return f"mongodb://{username}:{password}@{host}:27017"
        else:
            return None

    def store(self, data_to_store: IntermediateData) -> bool:
        pass


class SyncMongoStorageManager(MongoStorageManager):
    def __init__(self, conn_config: dict):
        super().__init__(conn_config=conn_config)
        self._init_storage()

    def _init_storage(self):
        """
        It creates a connection to the MongoDB database and creates a collection called AMRData
        """
        conn_string = self._create_conn_string()
        if conn_string:
            self.client = MongoClient(conn_string)
            db = self.client.bv_datastore
            self.collection = db.AMRData
            self.connected = True

    def store(self, data_to_store: IntermediateData) -> bool:
        """
        It takes an object of type IntermediateData, converts it to a dictionary, adds a timestamp, and then inserts it into
        the database

        :param data_to_store: The data to store in the database
        :type data_to_store: IntermediateData
        :return: A boolean value.
        """
        if self.connected:
            post = data_to_store
            post.timestamp = datetime.now()
            post = post.dict()
            self.collection.insert_one(post)
            return self.client.close() is None
        else:
            return False


class AsyncMongoStorageManager(MongoStorageManager):
    def __init__(self, conn_config: dict):
        super().__init__(conn_config=conn_config)

    async def _init_storage(self):
        conn_string = self._create_conn_string()
        if conn_string:
            self.client = motor_asyncio.AsyncIOMotorClient(conn_string)
            await init_beanie(database=self.client.bv_datastore, document_models=[AMRData])
            self.connected = True

    async def store(self, data_to_store: IntermediateData) -> bool:
        if not self.connected:
            await self._init_storage()

        if self.connected:
            mongo_data = AMRData.construct(typechecker_result=data_to_store.typechecker_result,
                                           conversion_result=data_to_store.conversion_result,
                                           validation_result=data_to_store.validation_result,
                                           calculation_result=data_to_store.calculation_result,
                                           visualizer_bytes=data_to_store.visualizer_bytes,
                                           error=data_to_store.error,
                                           timestamp=datetime.now())
            await mongo_data.insert()
            return self.client.close() is None
        else:
            return False


async def create_async_mongo_storage_manager(conn_config) -> MongoStorageManager:
    mongo_sm = AsyncMongoStorageManager(conn_config)
    await mongo_sm._init_storage()
    return mongo_sm


if __name__ == '__main__':
    class IntermediateDataFactory(ModelFactory[Any]):
        __model__ = IntermediateData

    data = IntermediateDataFactory.build()
    # mongo_storage_manager = SyncMongoStorageManager('test')
    # mongo_storage_manager.store(data)

    mongo_storage_manager = AsyncMongoStorageManager({'filename': ''})
    asyncio.run(mongo_storage_manager.store(data))

    # logging_storage_manager = LoggingStorageManager({'filename': 'log.txt'})
    # logging_storage_manager.store(data)
    #
    json_storage_manager = JsonStorageManager({'filename': 'log.json'})
    json_storage_manager.store(data)
