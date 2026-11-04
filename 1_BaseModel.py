"""
BaseModel - Foundation of Pydantic
BaseModel is the most fundamental element.

You create a class by inheriting from BaseModel.
"""

# Remember: BaseModel defines the structure, and Pydantic handles validation.

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    is_active: bool = True


# Validate Method 1
data = {"id": 1, "name": "Vikrant", "is_active": True}
userData = User(**data)
print(userData)

# Validate Method 2
userData1 = User(id=2, name="Kumar", is_active=False)
print(userData1)
print(userData1.id)
print(userData1.name)

##---------------Important operations---------------------

# Convert to dictionary
print("Use of model_dump() : ", userData1.model_dump())

# Convert to JSON
print("Use of model_dump_json() : ", userData1.model_dump_json())

# Validate dictionary
userData3 = User.model_validate(data)

# Validate JSON
userData4 = User.model_validate_json('{"id":3, "name":"V K", "is_active":true}') # use True -> true in this 
print("Validated JSON : ",userData4)

# Validate strings
userData5 = User.model_validate_strings({"id":"4", "name":"V K K", "is_active": "true"})
print("Validated JSON : ",userData5)