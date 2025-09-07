# This file manages application settings by loading them from environment variables
# using the pydantic-settings and python-decouple libraries.

from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):
    """
    Pydantic settings class that loads configuration from environment variables.
    This approach is a best practice for separating configuration from code.
    """
    # The database connection URL. 'config()' looks for 'DATABASE_URL' in the
    # environment, typically in a .env file.
    database_url: str = config('DATABASE_URL')
    
    # The expiration time for JWT access tokens in minutes.
    access_token_expire_minutes: int = 30
    
    # The secret key used for signing JWTs. This is loaded from the environment
    # to keep it secure and out of the source code.
    secret_key: str = config('SECRET_KEY')
    
    # The cryptographic algorithm used for JWTs.
    algorithm: str = "HS256"

    class Config:
        """
        Configuration for the Settings class.
        """
        # Specifies that settings should be loaded from a file named '.env'.
        env_file = '.env'
        # Ignores any environment variables that are not explicitly defined
        # as a field in the Settings class.
        extra = 'ignore'

# Create a single instance of the Settings class to be used throughout the application.
settings = Settings()
