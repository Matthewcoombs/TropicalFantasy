import re
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# This function returns the standard header for the majority of the Index
# API requests used
def standard_ix_api_header(token):
    """
    This is the standard header used in the majority of Index API Requests
    """
    headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer {}".format(token)
        }

    return headers


# This function loads and returns json/dictionary objects
def load_json(json_path):
    """
    This function loads and returns a json/dictionary object
    for the file passed as an argument
    """
    if type(json_path) != str:
        raise TypeError('Internal error - load_json() "json_path" argument must be type string')
    try:
        with open(json_path, 'r') as files:
            data = json.load(files)
            return data
    except Exception as error:
        raise error


# This function writes to json/dictionary objects
def write_to_json(key, value, json_path):
    """
    This function writes to a specified JSON file
    Key - A string value designated the key to enter
    Value - A value to set for the key passed
    """
    if type(key) != str and type(json_path) != str:
        raise TypeError('Internal error - write_to_json() "key" and "json_path" arguments must be type string')

    try:
        with open(json_path, 'r') as files:
            json_decoded = json.load(files)
            json_decoded[key] = value
        
        with open(json_path, 'w') as updated_json:
            json.dump(json_decoded, updated_json)
    except Exception as error:
        raise error


# This functions gathers returns an Index Exchange Application UI session cookies
def get_ui_session_cookies():
    """
    The username argument is the ix appAccount login used to login to system.indexexchange/app.indexexchange
    The password argument is the ix appAccount password

    This function will return the cookies from a login session in the Index Exchange Application
    """
    ui_login_credentials = load_json("api_services/json_files/auth_credentials.json")
    username = ui_login_credentials['SYSTEM_LOGIN']
    password = ui_login_credentials['SYSTEM_PASSWORD']
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(executable_path="api_services/utilities/chromedriver", options=chrome_options)
    driver.implicitly_wait(15)

    driver.get("https://system.indexexchange.com/login")
    driver.find_element_by_name("signIn").click()
    driver.find_element_by_name("signIn").click()
    driver.find_element_by_name("signIn").send_keys(username)
    driver.find_element_by_name("password").click()
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_xpath("/html/body/div/div[2]/div/div/div[2]/form/input").click()

    cookies = driver.get_cookies()
    driver.close()


    cookie_key_values = {cookie['name']: cookie['value'] for cookie in cookies}
    return cookie_key_values


# This function validates the custom library template form to ensure:
    # 1 - All necessary column headings are present
    # 2 - No duplicate HT Slot names exist on the sheet
    # 3 - ALL Flex Slots are comma delimited
    # 4 - All Banner slots contain sizes we support
    # 5 - ALL Video slots contain only ONE size
def template_validator(excel_template, headings, supported_sizes):
    """
    This function validates a given excel template, with a list of headings and supported
    Index Exchange Ad sizes

    The excel_template file is converted into a pandas dataframe and returned upon
    successful valiation
    """

    if type(headings) != list:
        raise TypeError('Internal error - template_validator() "headings" argument must be type list')
    
    # converting the excel_template into a pandas Dataframe
    try:
        template = pd.read_excel(excel_template)
    except:
        raise RuntimeError("There was an error handling the excel file: {}".format(excel_template.name))

    # Checking to ensure each heading is present on the loadsheet
    for heading in headings:
        try:
            template[heading]
        except:
            raise KeyError('The excel template is missing a "{}" column. Please enter this manually or download a template'.format(heading))

    if len(template.columns) == 6: 
        mapping_types = ["None", "divId", "divIdRegExBySize", "adUnitPathRegEx", "targeting"]
        if (template.columns[5] in mapping_types):
            if template.columns[5] == 'targeting':
                for index, targeting in enumerate(template['targeting']):
                    try:
                        for key_value_targeting in targeting.split(','):
                            print(key_value_targeting)
                            if not re.findall('.*=.*', key_value_targeting):
                                raise RuntimeError("Targeting on line {} does NOT follow proper formating".format(index + 2))
                    except:
                        raise RuntimeError("Targeting on line {} does NOT follow proper formating".format(index + 2))
        else:
            raise RuntimeError("The template is missing one of the following columns. Please add one: {}".format(mapping_types))
    
    # Initialising all headings here
    slotName_heading = headings[0]
    slotType_heading = headings[1]
    slotSizes_heading = headings[3]

    # Checking for duplicate values in the Slot Name Column
    slot_names = template[slotName_heading].duplicated()
    for index, duplicate_check in enumerate(slot_names):
        if duplicate_check == True:
            raise RuntimeError('HtSlot Name: "{}" on line {} is a duplicate entry'.format(template[slotName_heading][index], index + 2))

    # gather all index values for the banner and video slots provided
    bannerSlot_indexes = []
    videoSlot_indexes = []

    for index, slot_type in enumerate(template[slotType_heading]):
        if slot_type.upper() == "BANNER":
            bannerSlot_indexes.append(index)
        else:
            videoSlot_indexes.append(index)

    # This regex checks for all {width} x {height} sizes that are 1-4 digits
    regex = '\d{1,4}x\d{1,4}'
    ix_slot_count = 0
    # Checking all banner slots for Sizes Index Exchange Does NOT support
    for index in bannerSlot_indexes:

        # This block ensures all flex slots are comma delimited
        if template[slotSizes_heading][index].count('x') >= 2:
            if ',' not in template[slotSizes_heading][index]:
                raise RuntimeError("The Flex Slot on row {} requires comma delimited sizes".format(index + 2))


        sizes = re.findall(regex, template[slotSizes_heading][index])
        for size in sizes:
            if size not in supported_sizes:
                raise RuntimeError("The size: {} on line {} is not currently supported".format(size, index + 2))
            else:
                ix_slot_count += 1

    # Checking all Video slots To ensure they contain only ONE size
    if len(videoSlot_indexes) >= 1:
        for index in videoSlot_indexes:
            if template[slotSizes_heading][index].count('x') >= 2:
                raise RuntimeError("The video slot on line {} has more than one size".format(index + 2))
    
    if ix_slot_count > 100:
        raise RuntimeError('{} IX siteID slots detected. Please consolidate the template as the library currently supports a maximum of 100 slots'.format(ix_slot_count))
    # Returns the dataframe template if all checks pass without raising an error
    return template


# This function validates the siteID cloning template to ensure:
# 1 - There are no duplicate entrees listed
# 2 - No siteID currently exists with a name provided
def siteID_cloning_template_validator(excel_template):
    """
    This function validates a given excel template for siteID cloning

    The excel_template file is converted into a pandas dataframe and returned upon
    successful valiation
    """
    heading = 'SiteID Name(s)'
    # converting the excel_template into a pandas Dataframe
    try:
        template = pd.read_excel(excel_template)
    except:
        raise RuntimeError("There was an error handling the excel file: {}".format(excel_template.name))

    # Ensuring the proper column heading exists on the sheet
    try:
        template[heading]
    except:
        raise KeyError('The template is missing the required column heading "{}", please add this to your template and try again'.format(heading))

    # Checking for duplicate values in the siteID names(s) Column
    siteID_names = template[heading].duplicated()
    for index, duplicate_check in enumerate(siteID_names):
        if duplicate_check == True:
            raise RuntimeError('siteID name: "{}" on line {} is a duplicate entry'.format(template[heading][index], index + 2))
    
    return template


def delete_htSlots_template_validator(excel_template):
    """
    This function validates a given excel template for htSlot Deletion

    The excel_template file is converted into a pandas dataframe and returned upon
    successful valiation
    """

    """
    This function validates a given excel template for siteID cloning

    The excel_template file is converted into a pandas dataframe and returned upon
    successful valiation
    """
    heading = 'Slot Name'
    # converting the excel_template into a pandas Dataframe
    try:
        template = pd.read_excel(excel_template)
    except:
        raise RuntimeError("There was an error handling the excel file: {}".format(excel_template.name))

    # Ensuring the proper column heading exists on the sheet
    try:
        template[heading]
    except:
        raise KeyError('The template is missing the required column heading "{}", please add this to your template and try again'.format(heading))

    # Checking for duplicate values in the siteID names(s) Column
    htSlot_names = template[heading].duplicated()
    for index, duplicate_check in enumerate(htSlot_names):
        if duplicate_check == True:
            raise RuntimeError('siteID name: "{}" on line {} is a duplicate entry'.format(template[heading][index], index + 2))
    
    return template