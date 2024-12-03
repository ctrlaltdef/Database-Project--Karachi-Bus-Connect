import pyodbc

# Yusra's database
def database_connection():
    # Database connection configuration
    server = r'YUSRA\MYSQLSERVER1'
    database = 'KBusConnect'  # Name of your database
    use_windows_authentication = True  # Set to True for Windows Authentication
    username = 'your_username'  # Specify a username if not using Windows Authentication
    password = 'your_password'  # Specify a password if not using Windows Authentication

    # Create the connection string based on the authentication method chosen
    if use_windows_authentication:
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    else:
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    try:
        connection = pyodbc.connect(connection_string)
        return connection
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Tanzeel's database
# def database_connection():
#     # Database connection configuration
#     server = 'localhost'
#     database = 'KBusConnect'  # Name of your database
#     use_windows_authentication = False  # Set to True for Windows Authentication
#     username = 'sa'  # Specify a username if not using Windows Authentication
#     password = 'Fall2022.dbms'  # Specify a password if not using Windows Authentication

#     # Create the connection string based on the authentication method chosen
#     if use_windows_authentication:
#         connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
#     else:
#         connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

#     try:
#         connection = pyodbc.connect(connection_string)
#         return connection
#     except pyodbc.Error as e:
#         print(f"Error connecting to database: {e}")
#         return None
