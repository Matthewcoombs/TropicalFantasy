from mysql.connector import (connection)
from ..utilities.utility_function import load_json
from django.conf import settings
import json


class Viper2():

    def __init__(self):
        
        self.load_auth_credentials()




    def load_auth_credentials(self):
        """
        This method loads the auth credentials required to
        establish connection to the viper2 Database
        """

        if settings.ENVIRONMENT == 'local':
            credentials = load_json('api_services/json_files/mySQL_auth.json')
        elif settings.ENVIRONMENT == 'bartender':
            with open('/etc/indexexchange/auth.conf', 'r') as config_file:
                contents = config_file.read().encode("UTF-8")
                data = json.loads(contents)
                credentials = [credential['data'] for credential in data if credential['details'] == 'fred-viper2'][0]

        self.user = credentials["username"]
        self.password = credentials["key"]
        self.host = credentials["db_host"]
        self.database = credentials["db_name"]
    
    def get_locked_libraries(self, userID):
        """
        This method querys the Viper2 databae to retrieve all locked libraries
        for the given userID

        All locked configIDs will be returned in the form of a tuple
        """
        if type(userID) != int:
            raise TypeError("Internal error Viper2: The type of userID needs to be a 6 digit int")
        
        statement = "SELECT * FROM htwLocks WHERE userID = {};".format(userID)
            
        database = connection.MySQLConnection(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database
        )

        cursor = database.cursor()
        query = (statement)
        cursor.execute(query)

        locked_configurations = []
        for record in cursor:
            locked_configurations.append(record[3])
        
        cursor.close()
        locked_configurations = tuple(locked_configurations)
        return locked_configurations

    def get_account_siteIDs(self, userID, siteIDs=None):
        """
        This method runs a query into the Viper2 database to return records
        for account siteIDs

        If NO siteIDs are passed the query will return records containing all
        deleted and active siteIDs
        """

        if type(userID) != int:
            raise TypeError("The userID argument must be type integer")
        if type(siteIDs) != list and siteIDs != None:
            raise TypeError("The optional siteID argument must be type list")
        
        if siteIDs:
            if len(siteIDs) == 1:
                statement = 'SELECT * FROM sites WHERE userID = {} and siteID = {} and status = "A"'.format(userID, siteIDs[0])
            else:
                siteID_tuple = tuple([siteID for siteID in siteIDs])
                statement = 'SELECT * FROM sites WHERE userID = {} and siteID in {} and status = "A"'.format(userID, siteID_tuple)

        else:
            statement = 'SELECT * FROM sites WHERE userID = {} AND status = "A"'.format(userID)

        database = connection.MySQLConnection(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database
        )

        cursor = database.cursor()
        query = (statement)
        cursor.execute(query)

        siteIDs_to_return = [list(siteID[0:]) for siteID in cursor]
        cursor.close()

        return siteIDs_to_return