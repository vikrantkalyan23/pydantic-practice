# Pydantic in Depth

### Initialization

``` uv init ```

### Install Dependencies

``` uv add fastapi uvicorn pydantic pydandic-settings python-dotenv ```

### Install Existing Dependencies

``` uv sync ```

## 1. What is Pydantic? {#1-what-is-pydantic}

Pydantic is a Python library for validating, parsing, and serializing
data using Python type annotations. You define the expected shape of
data, then Pydantic checks incoming values and creates a validated
Python object.

It is commonly used for:

-   Validating HTTP request bodies, query parameters, and configuration.
-   Parsing JSON from external services, files, queues, and LLM
    responses.
-   Converting Python objects to dictionaries and JSON.
-   Defining nested data structures and constraints.
-   Generating JSON Schema for API documentation and integrations.

Pydantic v2 uses `pydantic-core` (implemented in Rust) for its core
validation and serialization engine.

## 2. Why do we need it? {#2-why-do-we-need-it}

Python type hints alone are primarily for documentation, IDE support,
and static analysis. They do not automatically validate values at
runtime.

For example, this annotation does not stop a caller from passing a
string as the age:

``` python
def create_user(name: str, age: int):
    return {"name": name, "age": age}

create_user("Asha", "not-a-number")  # Python itself allows this
```

Pydantic adds runtime validation:

``` python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str
    age: int = Field(ge=18, le=120)

user = UserCreate(name="Asha", age="28")
print(user.age)  # 28 (converted to int in the default lax mode)
print(user.model_dump())
```

Invalid data raises a `ValidationError`:

``` python
UserCreate(name="Asha", age=12)  # Fails: age must be at least 18
```

For inputs where implicit conversion is undesirable, configure strict
validation, for example with `ConfigDict(strict=True)` or strict field
types.

## 3. Main features {#3-main-features}

  Feature               What it does                                           Example use
  --------------------- ------------------------------------------------------ -----------------------------
  Runtime validation    Checks incoming values against declared types          API request body
  Type conversion       Converts compatible input values when allowed          `"25"` to `25`
  Field constraints     Enforces limits and formats                            `ge=0`, `max_length=100`
  Nested models         Validates complex objects                              Order containing line items
  Custom validators     Implements business-independent data rules             Validate a field format
  Serialization         Converts models into dictionaries or JSON              API response
  JSON Schema           Produces machine-readable schemas                      OpenAPI and integrations
  Settings management   Loads and validates environment/configuration values   Database URL and secrets

Pydantic validates data shape and declared constraints. It does **not**
replace business logic, database constraints, authorization, or security
checks.

## 4. Pydantic with FastAPI {#4-pydantic-with-fastapi}

FastAPI has first-class Pydantic integration. A request model documents
the expected payload, validates the request, and makes the validated
object available to the endpoint.

``` python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    age: int = Field(ge=18)

@app.post("/users")
def create_user(payload: UserCreate):
    return {
        "message": "User data is valid",
        "user": payload.model_dump()
    }
```

If the client sends invalid data, FastAPI returns a structured
validation error instead of requiring you to write repetitive checks in
every endpoint.

Typical flow:

``` text
HTTP request
    |
    v
FastAPI receives JSON
    |
    v
Pydantic validates and parses it
    |
    +---- invalid ----> HTTP 422 validation response
    |
    v
Endpoint receives a typed model
    |
    v
Application/service logic
    |
    v
Database or external service
```

## 5. Important Pydantic v2 methods {#5-important-pydantic-v2-methods}

  Method                             Purpose
  ---------------------------------- ----------------------------------------------------------
  `model_validate(data)`             Validate a Python object such as a dictionary
  `model_validate_json(json_data)`   Validate JSON text or bytes
  `model_dump()`                     Convert a model to Python data, usually a dictionary
  `model_dump_json()`                Serialize a model to a JSON string
  `model_json_schema()`              Generate JSON Schema
  `model_copy()`                     Create a copy of a model
  `field_validator`                  Add field-level validation
  `model_validator`                  Add model-level validation
  `TypeAdapter`                      Validate/serialize a type without defining a `BaseModel`

Example:

``` python
from pydantic import BaseModel, Field, field_validator

class ProductCreate(BaseModel):
    name: str = Field(min_length=2)
    price: float = Field(gt=0)
    sku: str

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("SKU cannot be empty")
        return value
```

## 6. Pydantic alternatives in the Python ecosystem {#6-pydantic-alternatives-in-the-python-ecosystem}

### 6.1 Comparison overview {#61-comparison-overview}

  Library         Main purpose                                                  Runtime validation                   Serialization                   JSON Schema Best suited for
  --------------- ---------------------------------------------- --------------------------------- ------------------------------- ----------------------------- -------------------------------------------------
  **Pydantic**    Data validation and serialization                                            Yes                             Yes                           Yes APIs, FastAPI, configuration, integrations
  `dataclasses`   Typed data containers (standard library)            No automatic type validation                    Basic/manual         No built-in generator Internal application objects
  `attrs`         Flexible class/data modeling                      Optional validators/converters   Usually with additional tools            Not its core focus Rich Python domain objects
  `msgspec`       Typed parsing, validation, and serialization                                 Yes                             Yes                           Yes High-throughput APIs and JSON workloads
  `marshmallow`   Schema-based validation and serialization                                    Yes                             Yes   Via extensions/integrations Explicit schemas and legacy systems
  `cattrs`        Structuring/unstructuring Python objects         Conversion and structure checks             Yes, via conversion            Not its core focus Dataclasses and attrs conversion
  `jsonschema`    Validate documents against JSON Schema                         Yes, schema-based             No model serializer              Uses JSON Schema Interoperability and externally defined schemas
  `typeguard`     Runtime checking of Python types                                Yes, type checks                              No                            No Testing and runtime type enforcement
  `beartype`      Runtime type-checking decorator                                 Yes, type checks                              No                            No Lightweight runtime checks

These tools overlap only partly. A runtime type checker such as
Typeguard is not a full replacement for a data parsing and serialization
library.

### 6.2 Pydantic vs dataclasses {#62-pydantic-vs-dataclasses}

**Standard-library dataclasses** create convenient classes for storing
structured data. They do not automatically validate annotations at
runtime.

``` python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

user = User(name="Asha", age="wrong")  # No automatic type validation
```

Pydantic equivalent:

``` python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# Raises ValidationError for incompatible input
user = User(name="Asha", age="wrong")
```

  Area                                 Dataclasses               Pydantic
  ------------------------------------ ------------------------- --------------------------------------------
  Built into Python                    Yes                       No
  Runtime type validation by default   No                        Yes
  Data conversion                      No automatic conversion   Yes, according to validation mode
  Serialization                        Basic/manual (`asdict`)   Built-in configurable dumping
  JSON Schema                          No built-in support       Yes
  Overhead                             Generally lower           More validation functionality and overhead

**Choose dataclasses** for trusted internal data structures. Choose
Pydantic when data crosses a boundary you do not control.

### 6.3 Pydantic vs attrs {#63-pydantic-vs-attrs}

`attrs` is a mature library for defining classes with less boilerplate.
It supports converters, validators, and many class-modeling features.

``` python
from attrs import define, field

@define
class User:
    name: str
    age: int = field(
        validator=lambda instance, attribute, value:
            (_ for _ in ()).throw(ValueError("Age must be positive"))
            if value <= 0 else None
    )
```

  Area                  attrs                          Pydantic
  --------------------- ------------------------------ --------------------------
  Main focus            Python class modeling          Boundary data validation
  Validators            Yes                            Yes
  Converters            Yes                            Yes
  JSON serialization    Additional tools/custom code   Built in
  JSON Schema           Not a primary feature          Built in
  FastAPI integration   Not native in the same way     First-class

**Choose attrs** for rich domain classes and flexible class behavior.
Choose Pydantic for API payloads, external data, and schema-driven
validation.

### 6.4 Pydantic vs msgspec {#64-pydantic-vs-msgspec}

`msgspec` is a strong alternative when performance is especially
important. It provides typed structures, validation, JSON
encoding/decoding, and JSON Schema generation.

``` python
import msgspec

class User(msgspec.Struct):
    name: str
    age: int

user = msgspec.json.decode(
    b'{"name":"Asha","age":28}',
    type=User
)
```

  Area                            msgspec                             Pydantic
  ------------------------------- ----------------------------------- ------------------------------------
  Runtime validation              Yes                                 Yes
  JSON decoding/encoding          Yes                                 Yes
  JSON Schema                     Yes                                 Yes
  Performance focus               Very high                           High
  Ecosystem/integrations          Smaller                             Broad
  FastAPI integration             Not the default native model path   First-class
  Flexible validation ecosystem   More focused                        Broad validators and customization

**Choose msgspec** for high-throughput serialization and parsing after
measuring your workload. Choose Pydantic for general-purpose backend
development and broad ecosystem compatibility.

Do not assume one is always faster for your application: benchmark
representative payloads and validation rules.

### 6.5 Pydantic vs Marshmallow {#65-pydantic-vs-marshmallow}

Marshmallow uses explicit schema classes to validate, deserialize, and
serialize data.

``` python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True, validate=validate.Range(min=18))

schema = UserSchema()
result = schema.load({"name": "Asha", "age": 28})
```

  Area                    Marshmallow                        Pydantic
  ----------------------- ---------------------------------- ------------------------------
  Schema definition       Separate schema classes            Python type-annotated models
  Validation              Yes                                Yes
  Serialization           Yes                                Yes
  Type-hint integration   Less central                       Core design
  JSON Schema             Usually via extensions             Built in
  FastAPI integration     Requires more manual integration   First-class

**Choose Marshmallow** if your project already uses it or you prefer
explicit schema definitions. For a new FastAPI project, Pydantic is
usually simpler.

### 6.6 Pydantic vs cattrs {#66-pydantic-vs-cattrs}

`cattrs` converts unstructured data (such as dictionaries) into
structured Python objects, commonly dataclasses or attrs classes, and
converts them back.

It is useful when you already model your domain with dataclasses or
attrs and need reliable conversion. It is not a direct all-in-one
substitute for Pydantic\'s validation, serialization, and JSON Schema
workflow.

### 6.7 Pydantic vs jsonschema {#67-pydantic-vs-jsonschema}

`jsonschema` validates a Python document against a JSON Schema document.

Use it when the schema itself comes from an external standard, partner,
or configuration file. Use Pydantic when you want to define the schema
naturally in Python and work with typed Python objects.

### 6.8 Pydantic vs Typeguard / Beartype {#68-pydantic-vs-typeguard--beartype}

Typeguard and Beartype check Python values against type annotations at
runtime. They are useful for catching type violations in function calls
and tests.

They are not designed to provide the same complete workflow as Pydantic
for parsing untrusted JSON, converting values, serializing models, and
generating API schemas.

## 7. Which one should you choose? {#7-which-one-should-you-choose}

  Your requirement                                 Recommended choice
  ------------------------------------------------ -------------------------
  Building a FastAPI REST API                      **Pydantic**
  Validating incoming JSON                         **Pydantic** or msgspec
  High-throughput JSON parsing                     Benchmark **msgspec**
  Simple internal data containers                  `dataclasses`
  Complex Python class modeling                    `attrs`
  Existing Marshmallow project                     Marshmallow
  Convert dictionaries to dataclasses/attrs        `cattrs`
  Validate against a third-party JSON Schema       `jsonschema`
  Runtime type checking in tests                   Typeguard or Beartype
  Environment variables and application settings   `pydantic-settings`

## 8. Recommended stack for a FastAPI backend {#8-recommended-stack-for-a-fastapi-backend}

For a new backend, a practical combination is:

``` text
FastAPI
  |
  +-- Pydantic v2
  |     +-- Request validation
  |     +-- Response schemas
  |     +-- Data serialization
  |     +-- JSON Schema
  |
  +-- pydantic-settings
  |     +-- Environment variables
  |     +-- Application configuration
  |
  +-- SQLAlchemy / SQLModel
  |     +-- Database models and persistence
  |
  +-- Alembic
        +-- Database migrations
```

Keep these responsibilities separate:

-   **Pydantic schemas:** validate API input and shape API output.
-   **ORM models:** represent and persist database records.
-   **Service layer:** implement business rules and workflows.
-   **Database constraints:** protect data integrity at the persistence
    layer.
-   **Authorization layer:** decide what the current user is allowed to
    do.

Avoid using one Pydantic model as your database model, create-request
model, update-request model, and public-response model when those
contracts have different security or lifecycle requirements.

A typical structure:

``` text
app/
├── main.py
├── core/
│   └── config.py
├── modules/
│   └── users/
│       ├── router.py
│       ├── schemas.py
│       ├── models.py
│       ├── service.py
│       └── repository.py
└── database/
    └── session.py
```

Example `schemas.py`:

``` python
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=12)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
```

Notice that the response schema does not expose the password.

## 9. Advantages and disadvantages of Pydantic {#9-advantages-and-disadvantages-of-pydantic}

### Advantages

-   Excellent FastAPI integration.
-   Type hints make schemas readable.
-   Strong nested data validation.
-   Built-in serialization and JSON Schema generation.
-   Custom validators and serializers.
-   Settings management through `pydantic-settings`.
-   Good IDE and static-analysis support.

### Disadvantages

-   Adds a dependency and runtime validation overhead.
-   Coercion in lax mode may be surprising if strict input is required.
-   Custom validators can become difficult to maintain if business logic
    is placed inside schemas.
-   Pydantic models are not database ORM models.
-   May be unnecessary for simple trusted internal objects.

## 10. Final recommendation {#10-final-recommendation}

For a modern Python backend:

1.  Use **Pydantic v2** for request/response schemas and external data
    validation.
2.  Use **pydantic-settings** for environment configuration.
3.  Use SQLAlchemy or SQLModel for database persistence.
4.  Use standard `dataclasses` for simple internal data containers where
    runtime validation is unnecessary.
5.  Evaluate **msgspec** only when profiling identifies serialization or
    validation as a meaningful performance bottleneck.
6.  Keep business rules in the service/domain layer rather than putting
    all application logic into Pydantic validators.

**Bottom line:** Pydantic is not simply a replacement for Python classes
or dataclasses. It is a validation and serialization layer that makes
untrusted data safer and easier to work with.