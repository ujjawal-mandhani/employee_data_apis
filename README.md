### Api Documentation of Employee

#### Getting Statrted

##### Prerequistes 

* Docker
* Docker Compose

##### Commands To set up locally

**Start the server**

```bash
docker-compose build 
docker-compose up -d
# In order to import admin data
docker exec -it mongodb mongoimport --db employee_data --collection employee_data_cllcn --file /home/data_import/import_data.json --jsonArray --username root --password example --authenticationDatabase admin
```
**Generate KeyFile**
 You can generate your own Key file or you can use this one as well mongo/config/keyfile

```bash
openssl rand -base64 756 > /data/configdb/keyfile
```
**Project test Cases**
```bash
docker exec -it fastapi pytest home/app/tests/test_app.py -p no:warnings -v
```

**Test Cases**

* incorrect_jwt_token_provided 
* expired_jwt_token_expired 
* authorization_is_not_provided 
* get_token_valid_employee 
* get_token_invalid_employee 
* get_employee_data_by_id 
* get_invalid_employee_data_by_id 
* admin_can_get_any_profile 
* non_admin_cannot_get_any_profile 
* individual_can_see_his_own_profile 
* admin_can_only_add_new_profile 
* admin_can_delete_any_profile 
* non_admin_can_not_delete_any_profile 
* can_not_delete_non_existing_profile 
* only_admin_get_paginated_data 
* non_admin_can_not_get_paginated_data 
* can_not_add_data_of_existing_email_id 
* can_not_update_email_existing_email 
* admin_can_update_details_of_individual 
* individual_can_update_details_of_individual