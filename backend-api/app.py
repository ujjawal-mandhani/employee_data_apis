import uuid
import datetime
from fastapi import FastAPI, Request, Response, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from Schemas.employee_schema import EmployeeSchemaAttributes, SuccessResponse, NotFoundResponse, InternalServerError, BadRequestResponse, ArrayEmployeeSchemaGetData, EmployeeSchemaGetData
from Exception_handler.exceptions import validation_exception_handler
from utility.utils import update_headers, get_headers, get_date_time, hash_password_func, generateJWTToken, verifyJWTToken, generate_id, generate_timenow_function
from utility.custom_logger import logger
from models.mongodb_connection import insert_document, find_data_in_mongo_db, delete_data_in_mongo_db, search_paginated, update_document


app = FastAPI()
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.get('/api/get_token/',  responses={
        200: {"model": SuccessResponse, "description": "Get Token"},
        404: {"model": NotFoundResponse, "description": "Employee not found"},
        500: {"model": InternalServerError, "description": "Internal Server Error"},
    })
async def get_token(request: Request, response: Response, employee_id: str = None):
    logger.info(f"::::employee id {employee_id}")
    employee_data = find_data_in_mongo_db("employee_data_cllcn", employee_id)
    try:
        if employee_data is None:
            return JSONResponse(
                status_code=404,
                content={
                    "message": "No Employee Data Found"
                },
                headers=get_headers()
            )
        jwt_payload = generateJWTToken(employee_id)
        return JSONResponse(
            status_code=200,
            content={
                "message": jwt_payload
            },
            headers=get_headers()
        )
    except Exception as E:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error"
            },
            headers=get_headers()
        )
        
@app.put("/api/employees/{id}/",  responses={
        200: {"model": SuccessResponse, "description": "Employee Details Updated"},
        404: {"model": NotFoundResponse, "description": "Employee not found"},
        500: {"model": InternalServerError, "description": "Internal Server Error"},
        400: {"model": BadRequestResponse, "description": "Bad request"},
    })
async def update_employee(id: str, request: Request, response: Response, employee_data_to_be_update: EmployeeSchemaAttributes, auth_token: str = Header(None)):
    id_to_be_updated = id
    authorization = auth_token
    if authorization is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Authorization is not present"
            },
            headers=get_headers()
        )
    admin_or_employee_id, message_jwt_token = verifyJWTToken(authorization)
    if message_jwt_token is not None:
        return JSONResponse(
            status_code=400,
            content={
                "message": message_jwt_token
            },
            headers=get_headers()
        )
    admin_or_employee_data = find_data_in_mongo_db("employee_data_cllcn", admin_or_employee_id)
    isadmin = admin_or_employee_data.get("employee_data").get('isadmin')
    old_employee_data = find_data_in_mongo_db("employee_data_cllcn", id_to_be_updated)
    if old_employee_data is None:
        return JSONResponse(
                status_code=400,
                content={
                    "message": f"unable to find data for id {id_to_be_updated}"
                },
                headers=get_headers()
            )
    old_employee_data.pop("_id")
    new_employee_data = employee_data_to_be_update.dict()
    new_employee_data["employee_data"]["employee_id"] = id_to_be_updated
    new_employee_data["employee_data"]["date_joined"] = old_employee_data["employee_data"].get("date_joined") or generate_timenow_function()
    if new_employee_data["employee_data"]["email"] != old_employee_data["employee_data"].get("email"):
        email_id_exists = find_data_in_mongo_db("employee_data_cllcn", new_employee_data["employee_data"]["email"], path="employee_data.email")
        if len(email_id_exists) > 1:
            return JSONResponse(
                    status_code=400,
                    content={
                        "message": "New Email already exist in database"
                    },
                    headers=get_headers()
                )
    try:
        if isadmin == "Y" or id_to_be_updated == admin_or_employee_id:
            update_document("employee_data_cllcn", id_to_be_updated, "employee_data.employee_id", new_employee_data)
            return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Profile Updated successfully"
                    },
                    headers=get_headers()
                )
        else:
            return JSONResponse(
                    status_code=404,
                    content={
                        "message": f"unable to find data for id {id_to_be_updated} or you do not have authorization to perform this action"
                    },
                    headers=get_headers()
                )
    except Exception as E:
        return JSONResponse(
            status_code=500,
            content={
                "message": str(E)
            },
            headers=get_headers()
        )
    
        
@app.get("/api/employees/", responses={
        200: {"model": ArrayEmployeeSchemaGetData, "description": "Get Paginated Data"},
        404: {"model": NotFoundResponse, "description": "Employee not found"},
        500: {"model": InternalServerError, "description": "Internal Server Error"},
        400: {"model": BadRequestResponse, "description": "Bad request"},
    })
async def get_paginated_employees(request: Request, response: Response, page_number: int = 1, page_size: int = 2, filter: str = None, auth_token: str = Header(None)):
    # headers = request.headers
    authorization = auth_token
    if authorization is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Authorization is not present"
            },
            headers=get_headers()
        )
    admin_or_employee_id, message_jwt_token = verifyJWTToken(authorization)
    if message_jwt_token is not None:
        return JSONResponse(
            status_code=400,
            content={
                "message": message_jwt_token
            },
            headers=get_headers()
        )
    admin_or_employee_data = find_data_in_mongo_db("employee_data_cllcn", admin_or_employee_id)
    isadmin = admin_or_employee_data.get("employee_data").get('isadmin')
    try:
        if admin_or_employee_data is not None and isadmin == "Y":
            pagnated_data = search_paginated("employee_data_cllcn", page_number, page_size, filter)
            return JSONResponse(
                    status_code=200,
                    content={
                        "message": pagnated_data
                    },
                    headers=get_headers()
                )
        else:
            return JSONResponse(
                    status_code=404,
                    content={
                        "message": f"you do not have authorization to perform this action"
                    },
                    headers=get_headers()
                )
    except Exception as E:
        return JSONResponse(
            status_code=500,
            content={
                "message": str(E)
            },
            headers=get_headers()
        )

@app.get("/api/employees/{id}/", responses={
        200: {"model": EmployeeSchemaGetData, "description": "Get Employee Data"},
        404: {"model": NotFoundResponse, "description": "Employee not found"},
        500: {"model": InternalServerError, "description": "Internal Server Error"},
        400: {"model": BadRequestResponse, "description": "Bad request"},
    })
async def search_employess(id: str, request: Request, response: Response, auth_token: str = Header(None)):
    id_to_be_searched = id
    # headers = request.headers
    authorization = auth_token
    if authorization is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Authorization is not present"
            },
            headers=get_headers()
        )
    logger.info(f"::::Id to be search {id_to_be_searched}")
    admin_or_employee_id, message_jwt_token = verifyJWTToken(authorization)
    if message_jwt_token is not None:
        return JSONResponse(
            status_code=400,
            content={
                "message": message_jwt_token
            },
            headers=get_headers()
        )
    # logger.info(f"::::Admin Employee ID {str(admin_employee_id)}")
    admin_or_employee_data = find_data_in_mongo_db("employee_data_cllcn", admin_or_employee_id)
    isadmin = admin_or_employee_data.get("employee_data").get('isadmin')
    employee_data = find_data_in_mongo_db("employee_data_cllcn", id_to_be_searched)
    try:
        if employee_data is not None and (isadmin == "Y" or id_to_be_searched == admin_or_employee_id):
            employee_data.pop("_id")
            return JSONResponse(
                    status_code=200,
                    content={
                        "message": employee_data
                    },
                    headers=get_headers()
                )
        else:
            return JSONResponse(
                    status_code=404,
                    content={
                        "message": f"unable to find data for id {id_to_be_searched} or you do not have authorization to perform this action"
                    },
                    headers=get_headers()
                )
    except Exception as E:
        return JSONResponse(
            status_code=500,
            content={
                "message": str(E)
            },
            headers=get_headers()
        )

@app.delete("/api/employees/{id}/",responses={
        200: {"model": SuccessResponse, "description": "Get Token"},
        404: {"model": NotFoundResponse, "description": "Employee not found"},
        500: {"model": InternalServerError, "description": "Internal Server Error"},
        400: {"model": BadRequestResponse, "description": "Bad request"},
    })
async def delete_employess(id: str, request: Request, response: Response, auth_token: str = Header(None)):
    id_to_be_deleted = id
    # headers = request.headers
    authorization = auth_token
    if authorization is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Authorization is not present"
            },
            headers=get_headers()
        )
    logger.info(f"::::Id to be deleted {id_to_be_deleted}")
    admin_or_employee_id, message_jwt_token = verifyJWTToken(authorization)
    if message_jwt_token is not None:
        return JSONResponse(
            status_code=400,
            content={
                "message": message_jwt_token
            },
            headers=get_headers()
        )
    # logger.info(f"::::Admin Employee ID {str(admin_employee_id)}")
    admin_or_employee_data = find_data_in_mongo_db("employee_data_cllcn", admin_or_employee_id)
    isadmin = admin_or_employee_data.get("employee_data").get('isadmin')
    employee_data = find_data_in_mongo_db("employee_data_cllcn", id_to_be_deleted)
    try:
        if employee_data is not None and isadmin == "Y":
            result = delete_data_in_mongo_db("employee_data_cllcn", id_to_be_deleted, "employee_data.employee_id")
            return JSONResponse(
                    status_code=204,
                    content={
                        "message": f"{id} deleted successfully"
                    },
                    headers=get_headers()
                )
        else:
            return JSONResponse(
                    status_code=404,
                    content={
                        "message": f"unable to find data for id {id_to_be_deleted} or You are not Admin"
                    },
                    headers=get_headers()
                )
    except Exception as E:
        return JSONResponse(
            status_code=500,
            content={
                "message": str(E)
            },
            headers=get_headers()
        )
        
@app.post('/api/employees/', responses={
        200: {"model": SuccessResponse, "description": "Get Token"},
        404: {"model": NotFoundResponse, "description": "Employee not found"},
        500: {"model": InternalServerError, "description": "Internal Server Error"},
        400: {"model": BadRequestResponse, "description": "Bad request"},
    })
async def create_employee(request: Request, response: Response, employee_data: EmployeeSchemaAttributes, auth_token: str = Header(None)):
    # headers = request.headers
    authorization = auth_token
    if authorization is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Authorization is not present"
            },# { "employee_data" : { "employee_id" : "d8b7cdd18bb64757ba0293179c4bbe79", "email" : "ujjawal.mandhani@canarahsbclife.in", "gender" : "M", "isadmin" : "Y", "name" : "Ujjawal Mandhani", "department" : "Sales", "role" : "Manager", "date_joined" : "2024-11-01 22:57:36.760759" } }
            headers=get_headers()
        )
    employee_data_inserted = employee_data.dict()
    employee_data_inserted_id = employee_data_inserted["employee_data"].get("employee_id")
    if employee_data_inserted_id is None or employee_data_inserted_id.strip() in [""]:
        employee_data_inserted["employee_data"]["employee_id"] = generate_id()
    employee_data_inserted["employee_data"]["date_joined"] = generate_timenow_function()
    # logger.info(f"::::Headers {str(headers["authorization"])}")
    admin_employee_id, message_jwt_token = verifyJWTToken(authorization)
    if message_jwt_token is not None:
        return JSONResponse(
            status_code=400,
            content={
                "message": message_jwt_token
            },
            headers=get_headers()
        )
    # logger.info(f"::::Admin Employee ID {str(admin_employee_id)}")
    admin_data = find_data_in_mongo_db("employee_data_cllcn", admin_employee_id)
    if admin_data is None:
        return JSONResponse(
            status_code=400,
            content={
                "message": "You are not Admin"
            },
            headers=get_headers()
        )
    # logger.info(f"::::Admin Data {str(admin_data)}, {admin_data.get("employee_data").get('isadmin')}")
    try:
        isadmin = admin_data.get("employee_data").get('isadmin')
        # isadmin = 'Y' # This is for inserting first time admin
        if isadmin == "Y":
            status_code, err_mssg = insert_document("employee_data_cllcn", employee_data_inserted, ["employee_data.email", "employee_data.employee_id"])
            return JSONResponse(
                status_code=status_code,
                content={
                    "message": str(err_mssg)
                },
                headers=get_headers()
            )
        else:
            raise Exception("You are not Admin")
    except Exception as E:
        return JSONResponse(
            status_code=500,
            content={
                "message": str(E)
            },
            headers=get_headers()
        )
        
