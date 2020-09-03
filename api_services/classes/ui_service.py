import json
import requests
from ..utilities.utility_function import (load_json, 
                                          write_to_json, 
                                          standard_ix_api_header)

class AppAccount(object):
    """
    This is the class based app account model. The majority of functions and services
    related to the app account will be set here
    """
    def __init__(self, userID):
        self.userID = userID
        self.load_authorization_credentials()
        self.api_token_generator()

    
    # Loading the necessary authorization credentials
    def load_authorization_credentials(self):
        """
        This method loads all necessary authorization credentials
        """
        try:
            if __name__ == "__main__":
                credentials = load_json('auth_credentials.json')
            else:
                credentials = load_json('api_services/json_files/auth_credentials.json')
        except Exception as error:
            raise error
             

        self.api_key = credentials["API_KEY"]
        self.ui_login = credentials["UI_LOGIN"]


    # The general function for generating an Index API token
    def api_token_generator(self):
        """
        This method generates an api_token for general api usage
        """
        headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-cache"
        }

        payload = {
        "username": self.ui_login,
        "key": self.api_key
        }

        response = requests.post(url = "https://auth.indexexchange.com/auth/oauth/token",
                                 data = json.dumps(payload), 
                                 headers = headers)
        json_data = response.json()

        if json_data['responseCode'] != 200:
            raise RuntimeError('Please check the auth_credentials.json file')

        else:
            self.token = json_data['data']['accessToken']
            return self.token


    # This functions loads ALL front-end library configurations for the given application account
    def get_wrappers_service(self):
        """
        This method returns all wrapper configurations for the current Index App Account
        """
        response = requests.get(url="https://api01.indexexchange.com/api/headertag/wrapper/configs?userID={}".format(self.userID),
                                headers = standard_ix_api_header(self.token))
        data = response.json()
        try:
            if len(data['data']) < 1:
                print("This is not an Index Exchange Headerbidding Wrapper Account")
                print("No wrapper objects have been loaded")
                return None
            else:
                # Loading all non-deleted libraries
                self.wrappers = [library for library in data['data'] if library['status'] == 'A']
                return self.wrappers

        except Exception as error:
            raise error


    # This function updates the given wrapper object's front-end configuration
    def update_wrappers_service(self, wrapper_object):
        """
        This method updates the desired wrapper_object passed to it
        """
        # The wrapper 'status' key:value pairing must be removed in order to update
        # the wrapper configuration
        try:
            del wrapper_object['status']

            # The entire wrapper object must be passed in the request body
            payload = wrapper_object
            response = requests.put(url ="https://api01.indexexchange.com/api/headertag/wrapper/configs",
                                    data=json.dumps(payload), 
                                    headers=standard_ix_api_header(self.token))
            data = response.json()
            if data['responseCode'] != 200:
                print('{} failed to update'.format(wrapper_object['name']))
                print(data)
                raise RuntimeError("update_wrappers_service job failed: \n{}".format(data))
            elif data['responseCode'] == 200:
                print('{} was updated succesfully'.format(wrapper_object['name']))
                return data
        except Exception as error:
                raise error

        
    # This function launches a single wrapper in the desired app account
    def launch_wrapper_service(self, wrapper_object, launch_type):
        """
        This method launches wrapper configurations for the app-account set

        The 'launch_type' argument will only accept two string values:
        'staging' or 'production'

        succesfull launches will return a 1(int) value
        failed launched will return a 0(int) value
        """
        if type(launch_type) != str:
            raise TypeError('the "launch_type" argument must be a string')

        if launch_type != 'staging' and launch_type != 'production':
            raise ValueError('The launch_type argument must be "staging" or "production"')
            
        payload = {
        "userID": self.userID,
        "configID": wrapper_object['configID'],
        "buildTo": launch_type
        }

        response = requests.put(url="https://api01.indexexchange.com/api/headertag/wrapper/files", 
                                data= json.dumps(payload), 
                                headers=standard_ix_api_header(self.token))
        data = response.json()
        if data['responseCode'] != 200:
            print('{} Failed to launch to {}'.format(wrapper_object['name'], launch_type))
            raise RuntimeError("launch_wrapper_service job failed")
        else:
            print('{} Was launched to {}'.format(wrapper_object['name'], launch_type))
            return data['data']


    # This is the general blocking function/service utilised on AppAccount SiteIDs
    def set_siteID_blocks_service(self, block_type, typeIDs, status, siteIDs=None):
        """
        This method formats the general blocking requests on Index AppAccount
        siteIDs

        For information on formatting specific payload parameters please see the following sources:
        https://kb.indexexchange.com/apis/publisherapi.htm#block-brand-criteria
        https://kb.indexexchange.com/apis/publisherapi.htm#block-brands
        https://kb.indexexchange.com/apis/publisherapi.htm#block-buyers
        https://kb.indexexchange.com/apis/publisherapi.htm#block-dsps
        https://kb.indexexchange.com/apis/publisherapi.htm#block-trading-desks

        Note:
        All requests upon success enter a queue
        The majority of requests can perform bulk updates of siteIDs
        Not all endpoints are documented and will require reverse engineering to uncover
        """
        # The following blocks checks if each argument passes the correct information
        if status!= 1 and status != 0:
            raise ValueError('The "status" argument must be 1 or 0')

        if type(siteIDs) != list and type(typeIDs) != list:
            raise TypeError('The "siteIDs" and "typeIDs" arguments must be a list')
        
        available_types = ['siteDSPBlock', 'siteTradingDeskBlock', 'siteBuyerBlock', 
                           'siteBrandBlock', 'siteBrandCriteriaBlock', 'siteIndustryBlock',
                           'siteCreativeTypeBlock', 'siteContentGroupBlock']
        if block_type not in available_types:
            raise ValueError('The available blocking types must be one of the following values: {}'.format(available_types))

        # If no siteIDs are passed all siteIDs will be set in the payload
        if siteIDs == None:
            siteIDs = [siteID['siteID'] for siteID in self.get_siteIDs_service()]
            

        # This block determines the label for the typeIDs list argument inside of the payload
        if block_type == 'siteDSPBlock':
            id_label = 'dspID'
        elif block_type == 'siteTradingDeskBlock':
            id_label = 'tradingDesk'
        elif block_type == 'siteBuyerBlock':
            id_label = 'buyerID'
        elif block_type == 'siteBrandBlock':
            id_label = 'brandID'
        elif block_type == 'siteIndustryBlock':
            id_label = 'siteTagID'
        elif block_type == 'siteCreativeTypeBlock':
            id_label = 'siteTagID'
        elif block_type == 'siteContentGroupBlock':
            id_label = 'contentID'
        else:
            id_label = 'criteriaID'

        # Formatting the request payload
        payload = {
            "userID": self.userID,
            "task": block_type,
            "data": [
                {
                    "value": status,
                    "siteID": siteIDs,
                    id_label: typeIDs
                }
            ]
        }

        response = requests.put(url = 'https://api01.indexexchange.com/api/tasks',
                                data = json.dumps(payload),
                                headers = standard_ix_api_header(self.token))
        
        data = response.json()
        if data['responseCode'] == 202:
            print('The requested {} is succesfully queued'.format(payload['task']))
        elif data['responseCode'] != 202:
            print(data)
            raise RuntimeError("set_siteID_blocks_service job failed")


    # This function returns all or a specified amount of siteID objects
    def get_siteIDs_service(self, siteID=None):
        """
        This method returns all siteIDs along with the ID's respective 
        details for the current Index App Account

        If the optional siteID argument is passed, the IDs must be in a
        list format
        """
        # If no siteIDs are passed the payload will be formatted to return ALL siteIDs
        if siteID == None:
            payload = {
                "userID": self.userID
            }
        else:
            if type(siteID) != list:
                raise TypeError("The siteID argument must be a list")
            else:
                payload = {
                    "userID": self.userID,
                    "siteID": siteID
                }

        response = requests.post(url = "https://api01.indexexchange.com/api/publishers/sites", 
                                 data = json.dumps(payload), 
                                 headers = standard_ix_api_header(self.token))
        data =  response.json()
        if data['responseCode'] != 200:
            print(data)
            raise RuntimeError('get_siteIDs_service job failed')
        else:
            return data['data']


    # This function updates the category for a given siteID provided
    def update_siteID_category(self, siteID, categoryID):
        """
        This method updates the category for the given siteID
        the siteID argument passed by a type: list
        the categoryID provided must be a type: int

        See Index API documentation:
        https://kb.indexexchange.com/apis/publisherapi.htm#update-site-tag
        https://kb.indexexchange.com/apis/publisherapi.htm#get-site-categories
        """
        if type(siteID) != int or type(categoryID) != int:
            raise TypeError("The siteID and categroyID arguments must be an integer")

        payload = {
            "userID": self.userID,
            "siteID": siteID,
            "siteTagCategory": categoryID
        }

        response = requests.patch(url="https://api01.indexexchange.com/api/publishers/sites",
                                  data=json.dumps(payload),
                                  headers=standard_ix_api_header(self.token))
        data = response.json()
        if data['responseCode'] != 200:
            print(data)
            raise RuntimeError("update_siteID_category job failed")
        else:
            print('\n{} category updated succesfully'.format(siteID))
            print(data['data'])


    # Loading the app account details
    def get_account_info_service(self):
        """
        This function loads all app-account details
        """

        response = requests.get(url="https://api01.indexexchange.com/api/users/profile?userID={}".format(self.userID),
                                headers = standard_ix_api_header(self.token))
        if response.status_code != 200:
            raise RuntimeError("Failed to retrieve {} account information".format(self.userID))
        
        data = response.json()
        account_details = {key:data['data'][key] for key in data['data']}

        return account_details