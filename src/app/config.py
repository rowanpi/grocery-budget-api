from pydantic import BaseSettings
from typing import Set

class Settings(BaseSettings):
    grocery_budget_api_db_user_name: str = "postgres"
    grocery_budget_api_db_password: str = ""
    grocery_budget_api_db_name: str = "grocery_budget"
    grocery_budget_api_db_port = 5432
    grocery_budget_api_db_host = "localhost"

    grocery_budget_app_port = 8000
    grocery_budget_secret_key: str = "secret_key"
    grocery_budget_token_expiry_minutes: int = 20
    grocery_budget_refresh_token_expiry_minutes: int = 60 * 24 * 31
    grocery_budget_media_item_store: str = "local" # local or s3 (aws)
    grocery_budget_media_item_base_path: str = "./media_items"

    grocery_budget_cors_origins: Set[str] = set()
    grocery_budget_cors_origins.add("http://localhost:3000")


    grocery_budget_s3_bucket_name = "grocerybudget"
    grocery_budget_s3_region_name = "eu-west-1"
    grocery_budget_s3_access_key = ""
    grocery_budget_s3_secret_access_key = ""

    grocery_budget_google_client_id = "1026317288648-ig69iuhplrskjvuqtov66qu4bihlk27g.apps.googleusercontent.com"


    class Config:
        env_file = ".env"

settings = Settings()
