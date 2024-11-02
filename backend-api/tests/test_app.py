from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_incorrect_jwt_token_provided():
    id_to_be_searched= "123456"
    jwt_key = "wrong_jwt"
    response = client.get(f"/api/employees/{id_to_be_searched}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 400
    assert eror_messg == "Invalid token"
    
def test_expired_jwt_token_expired():
    id_to_be_searched= "123456"
    jwt_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlbXBsb3llZV9pZCIsImlzcyI6ImVtcGxveWVlX2lkIHRva2VuIGdlbmVyYXRpb24iLCJlbXBsb3llZWlkIjoiMTIzNDU2IiwiZXhwIjoxNzMwNTI1NDcxfQ.D22p0t4Cr16w7oe2VU_owKMNfFqwFwIIUc9e0nxzZLc"
    response = client.get(f"/api/employees/{id_to_be_searched}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 400
    assert eror_messg == "Token has expired"
    
# Authorization is not present
def test_authorization_is_not_provided():
    id_to_be_searched= "123456"
    response = client.get(f"/api/employees/{id_to_be_searched}/")
    print(response.json())
    eror_messg = response.json()["message"]
    assert response.status_code == 400
    assert eror_messg == "Authorization is not present"

def test_get_token_valid_employee():
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    json_response = response.json()
    assert response.status_code == 200
    assert "message" in json_response
    
def test_get_token_invalid_employee():
    response = client.get("/api/get_token/", params={"employee_id": "12345678910"})
    json_response = response.json()
    assert response.status_code == 404
    assert json_response["message"] == "No Employee Data Found"
    
def test_get_employee_data_by_id():
    jwt_key = client.get("/api/get_token/", params={"employee_id": "123456"}).json()["message"]
    response = client.get("/api/employees/123456/", headers={"auth-token": jwt_key})
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["message"] == { "employee_data" : { "employee_id" : "123456", "email" : "ujjawalmandhani97858@gmail.com", "gender" : "M", "isadmin" : "Y", "name" : "8pL", "department" : "Engineering", "role" : "Manager" } }
    
def test_get_invalid_employee_data_by_id():
    id_to_be_searched= "123456789"
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.get(f"/api/employees/{id_to_be_searched}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 404
    assert eror_messg == f"unable to find data for id {id_to_be_searched} or you do not have authorization to perform this action"
    
def test_admin_can_get_any_profile():
    id_to_be_searched= "067a6c28432c4169b6bf1cf745575c17"
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.get(f"/api/employees/{id_to_be_searched}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 200
    assert eror_messg == { "employee_data" : { "employee_id" : "067a6c28432c4169b6bf1cf745575c17", "email" : "aupermandhani97859@gmail.com", "gender" : "M", "isadmin" : "N", "name" : "Ujjawal Mandhani", "department" : "Engineering", "role" : "Manager" }}

def test_non_admin_cannot_get_any_profile():
    id_to_be_searched= "123456"
    response = client.get("/api/get_token/", params={"employee_id": "067a6c28432c4169b6bf1cf745575c17"})
    jwt_key = response.json()["message"]
    response = client.get(f"/api/employees/{id_to_be_searched}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 404
    assert eror_messg == f"unable to find data for id {id_to_be_searched} or you do not have authorization to perform this action"
    
def test_individual_can_see_his_own_profile():
    id_to_be_searched= "067a6c28432c4169b6bf1cf745575c17"
    response = client.get("/api/get_token/", params={"employee_id": "067a6c28432c4169b6bf1cf745575c17"})
    jwt_key = response.json()["message"]
    response = client.get(f"/api/employees/{id_to_be_searched}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 200
    assert eror_messg == { "employee_data" : { "employee_id" : "067a6c28432c4169b6bf1cf745575c17", "email" : "aupermandhani97859@gmail.com", "gender" : "M", "isadmin" : "N", "name" : "Ujjawal Mandhani", "department" : "Engineering", "role" : "Manager" }}

def test_admin_can_only_add_new_profile():
    profile_to_be_added = { "employee_data" : { "employee_id" : "d8b7cdd18bb64757ba0293179c4bbe79", "email" : "ujjawal.mandhani@canarahsbclife.in", "gender" : "M", "isadmin" : "Y", "name" : "Ujjawal Mandhani", "department" : "Sales", "role" : "Manager"} }
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.post(f"/api/employees/", json={"employee_data": profile_to_be_added["employee_data"]}, headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 201
    assert eror_messg == f"data Inserted successfully"

def test_admin_can_delete_any_profile():
    id_to_be_delete = "d8b7cdd18bb64757ba0293179c4bbe79"
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.delete(f"/api/employees/{id_to_be_delete}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 204
    assert eror_messg == f"{id_to_be_delete} deleted successfully"

def test_non_admin_can_not_delete_any_profile():
    id_to_be_delete = "1234567"
    response = client.get("/api/get_token/", params={"employee_id": "1234567"})
    jwt_key = response.json()["message"]
    response = client.delete(f"/api/employees/{id_to_be_delete}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 404
    assert eror_messg == f"unable to find data for id {id_to_be_delete} or You are not Admin"

def test_can_not_delete_non_existing_profile():
    id_to_be_delete = "1234567_blah_blah"
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.delete(f"/api/employees/{id_to_be_delete}/", headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 404
    assert eror_messg == f"unable to find data for id {id_to_be_delete} or You are not Admin"
    
def test_only_admin_get_paginated_data():
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.get(f"/api/employees/", params={"page_number": 1, "page_size": 2, "filter": "Engineering"}, headers={"auth-token": jwt_key})
    eror_messg = response.json()
    print(eror_messg)
    assert response.status_code == 200
    assert eror_messg == { "message": [ { "employee_data": { "employee_id": "123456", "email": "ujjawalmandhani97858@gmail.com", "gender": "M", "isadmin": "Y", "name": "8pL", "department": "Engineering", "role": "Manager" } }, { "employee_data": { "employee_id": "c09ed4e39b014a89b4bf79eef2b2ecdb", "email": "supermandhani@gmail.com", "gender": "M", "isadmin": "N", "name": "Ujjawal Mandhani", "department": "Engineering", "role": "Manager" } } ] }

def test_non_admin_can_not_get_paginated_data():
    response = client.get("/api/get_token/", params={"employee_id": "1234567"})
    jwt_key = response.json()["message"]
    response = client.get(f"/api/employees/", params={"page_number": 1, "page_size": 2, "filter": "Engineering"}, headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    print(eror_messg)
    assert response.status_code == 404
    assert eror_messg == "you do not have authorization to perform this action"

def test_can_not_add_data_of_existing_email_id():
    profile_to_be_added = { "employee_data" : { "employee_id" : "1234567", "email" : "ujjawal.mandhani@lumiq.ai", "gender" : "M", "isadmin" : "N", "name" : "Ujjawal Mandhani", "department" : "Engineering", "role" : "Manager"} }
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.post(f"/api/employees/", json={"employee_data": profile_to_be_added["employee_data"]}, headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    assert response.status_code == 400
    assert eror_messg == "Attribute " + "employee_data.email" + " existing in databse with value " + "ujjawal.mandhani@lumiq.ai"
    
def test_can_not_update_email_existing_email():
    id_to_be_update = "786910"
    profile_to_be_added = { "employee_data" : { "employee_id" : "786910", "email" : "ujjawal.mandhani@lumiq.ai", "gender" : "F", "isadmin" : "Y", "name" : "Ujjawal Mandhani", "department" : "Engineering", "role" : "Analyst"} }
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.put(f"/api/employees/{id_to_be_update}/", json={"employee_data": profile_to_be_added["employee_data"]}, headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    print(eror_messg)
    assert response.status_code == 400
    assert eror_messg == "New Email already exist in database"
    
def test_admin_can_update_details_of_individual():
    id_to_be_update = "786910"
    profile_to_be_added = { "employee_data" : { "employee_id" : "786910", "email" : "new_test_email@gmail.com", "gender" : "F", "isadmin" : "Y", "name" : "Ujjawal Mandhani", "department" : "Engineering", "role" : "Developer"} }
    response = client.get("/api/get_token/", params={"employee_id": "123456"})
    jwt_key = response.json()["message"]
    response = client.put(f"/api/employees/{id_to_be_update}/", json={"employee_data": profile_to_be_added["employee_data"]}, headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    print(eror_messg)
    assert response.status_code == 200
    assert eror_messg == "Profile Updated successfully"
    
def test_individual_can_update_details_of_individual():
    id_to_be_update = "786910"
    profile_to_be_added = { "employee_data" : { "employee_id" : "786910", "email" : "new_test_email@gmail.com", "gender" : "F", "isadmin" : "Y", "name" : "Ujjawal Mandhani", "department" : "Engineering", "role" : "Analyst"} }
    response = client.get("/api/get_token/", params={"employee_id": "786910"})
    jwt_key = response.json()["message"]
    response = client.put(f"/api/employees/{id_to_be_update}/", json={"employee_data": profile_to_be_added["employee_data"]}, headers={"auth-token": jwt_key})
    eror_messg = response.json()["message"]
    print(eror_messg)
    assert response.status_code == 200
    assert eror_messg == "Profile Updated successfully"