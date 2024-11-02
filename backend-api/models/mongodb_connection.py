from pymongo import MongoClient
from utility.custom_logger import logger


client = MongoClient(f"mongodb://root:example@mongo:27017/")
db_name = "employee_data"

def insert_document(collection_name, data, parameters_to_check):
    err_mssg = "data Inserted successfully"
    try:
        db = client[db_name]
        collection = db[collection_name]
        for attribute in parameters_to_check:
            attribute_arry = attribute.split('.')
            final_data = None
            for item in attribute_arry:
                final_data = final_data.get(item) if final_data is not None and type(final_data).__name__ == 'dict' else data.get(item)
            query = {attribute: final_data}
            exists = collection.find_one(query) is not None
            if exists:
                err_mssg = "Attribute " + attribute + " existing in databse with value " + final_data
                logger.info(err_mssg)
                raise Exception(err_mssg)
        collection.insert_one(data)
        return 201, err_mssg
    except Exception as E:
        logger.error("::::Error while inserting data")
        logger.info(E)
        return 400, E

def find_data_in_mongo_db(collection_name, id, path="employee_data.employee_id"):
    db = client[db_name]
    collection = db[collection_name]
    query = {path: id}
    data_in_mongo_db = collection.find_one(query)
    return data_in_mongo_db

def delete_data_in_mongo_db(collection_name, id, path):
    db = client[db_name]
    collection = db[collection_name]
    result = collection.delete_one({path: id})
    return result.deleted_count

def search_paginated(collection_name, page_number, page_size, filter):
    default_page_size = 10 if page_size > 10 else page_size 
    db = client[db_name]
    collection = db[collection_name]
    skip = (page_number - 1) * default_page_size
    if filter is not None:
        query = {"employee_data.department": filter}
        results = list(collection.find(query).skip(skip).limit(default_page_size))
    else:
        results = list(collection.find().skip(skip).limit(default_page_size))
    for item in results:
        item.pop("_id")
    return results

def update_document(collection_name, employee_id, path, new_data):
    delete_data_in_mongo_db(collection_name, employee_id, path)
    status_code, error_message = insert_document(collection_name, new_data, ["employee_data.email", "employee_data.employee_id"])
    return status_code, error_message