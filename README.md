# Pydantic in Depth

In the Python ecosystem, Pydantic is primarily used for data validation, parsing, serialization, and type safety. Pydantic Settings is used to manage application configuration and environment variables.

## What does Pydantic provide

``` 
Feature	                        Purpose

Type validation	            Validate string, integer, boolean, etc.
Required fields	            Ensure mandatory fields exist
Default values	            Set defaults for optional fields
Custom validation	    Apply business-specific rules
Nested models	            Validate complex JSON structures
Serialization	            Convert objects into dictionaries or JSON
Type conversion	            Convert compatible input types
JSON Schema	              Generate schemas for API documentation

```

# Initialization

``` uv init ```

# Install Dependencies

``` uv add fastapi uvicorn pydantic pydandic-settings python-dotenv ```

# Install Existing Dependencies

``` uv sync ```

