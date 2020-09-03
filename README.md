# Tropical Fantasy
Tropical Fantasy is an internal application built primarily for the
Solutions Consulting/Operations team to automate some of the day to day
tasks. It focuses primarily on tasks revolving around the Index Application
UI.

# Setup:
1. You must have atleast python3 installed
2. (Optional) It is recommended, but not required that you run this application
in a virtual environment. Reference:https://virtualenv.pypa.io/en/latest/
3. Install all necessary dependencies listed in the `requirements.txt` file.
Run `pip install -r requirements.txt`
4. Enable backend services by providing authentication credentials the Index
Exchange API. Inside of `api_services/json_files` create a json file called
`auth_credentials.json`. In this file add the following keys...
- `UI_LOGIN` - The login used for app.indexexchange or system.indexexchange
- `API_KEY` - The API key associated with the UI login email provided
- `SYSTEM_LOGIN` - The login used for system.indexexchange only
- `SYSTEM_PASSWORD` - The password used for the system.indexexchange account
5. Enable backend connections to the Viper2 mySQL database. Create a json file
inside of `api_services/json_files` called `mySQL_auth.json`. In this file add
the following keys...
- `username` - The user name of the account with access to Viper2
- `key` - The key or password associated to the account
- `db_host` - The IP address of the slave Viper2 DB
- `db_name` - The name of the database currently being read from. Usually `Viper2`

# Starting the Server
In the main directory of this application enter the following commands in
your terminal...

1. Local Instance
- To run the application locally enter `python manage.py runserver --settings=ix_api_tool.environments.local`
2. Production/Bartender
- To run the application in production/on the bartender vm enter
`python manage.py runserver --settings=ix_api_tool.environments.bartender`

# Stop Server
`CTRL-C` Easy as 1,2,3...