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

# Method 1
data = {"id": 1, "name": "Vikrant", "is_active": True}
userData = User(**data)
print(userData)

# Method 2
userData1 = User(id= 2, name= "Kumar", is_active= False)
print(userData1)
