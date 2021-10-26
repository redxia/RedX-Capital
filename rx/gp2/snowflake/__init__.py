from .__snowflake import (

    get_credentials,
    connect,
    disconnect,
    get_sqlalchemy_connection_string,

    execute,
    fetchall,
    fetchall_simple,
    fetchone
)

def __getattr__(name):
    if name == 'conn': return __snowflake.conn
    elif name == 'cursor': return __snowflake.connect().cursor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
