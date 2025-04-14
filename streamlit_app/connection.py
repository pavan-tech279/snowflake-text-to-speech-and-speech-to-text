from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session

def create_snowflake_session():
    session = get_active_session()
    return session 