import re
import asyncio
import aiohttp
from ..classes.viper2 import Viper2
from ..classes.ui_service import AppAccount
from ..utilities.utility_function import (load_json,
                                          standard_ix_api_header,
                                          get_ui_session_cookies,
                                          siteID_cloning_template_validator
                                          )

# This function sets the standard blocks list across all siteIDs
# submitted in the 'siteID_list' argument
# Standard Block List: https://confluence.indexexchange.com/display/CSM/Usual+Block+List
def set_standard_blocks(userID, siteID_list, job_status):
    """
    This functions sets the standard or Usual Blocklist on
    all siteID objects passed
    """
    if not isinstance(siteID_list, list):
        raise TypeError('set_standard_blocks(): the siteID_list argument must be of type list')
    if not isinstance(userID, int):
        raise TypeError('set_standard_blocks(): the userID argument must be of type int')
    if job_status != 0 and job_status != 1:
        raise ValueError('set_standard_blocks(): The job_status argument must be 1(on) or 0(off)')


    # initialising the AppAccount class
    myAccount = AppAccount(userID)

    # This block checks to see if the siteID object(s)
    # passed belong to the AppAccount passed
    data = myAccount.get_siteIDs_service()
    appAccount_siteID_list = [siteID['siteID'] for siteID in data]

    for siteID in siteID_list:
        if siteID not in appAccount_siteID_list:
            unauthorized_siteID = siteID
            raise RuntimeError('UserID {} does not own siteID: {}'.format(myAccount.userID, unauthorized_siteID))
        
    #Setting a dictionary containing key-values pairs of the usual block list
    standard_blocks = {
        "siteIndustryBlock": [6579, 6627, 6631, 6637, 7228, 8138, 8139, 8140, 8141, 8167, 8168, 8154, 8169, 8144, 8145, 8146, 8166, 8148, 8149],
        "siteCreativeTypeBlock": [8133],
        "siteContentGroupBlock": [11, 18, 32, 34, 36, 48]
        }


    async def create_put_data(userID, standard_blocks, status, siteIDs):
        for block_type, typeIDs in standard_blocks.items():
            # This block determines the label for the typeIDs list argument inside of 
            # the payload
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

            yield {
            "userID": userID,
            "task": block_type,
            "data": [
                {
                    "value": status,
                    "siteID": siteIDs,
                    id_label: typeIDs
                }
            ]
        }


    async def batch_requests():
        async with aiohttp.ClientSession(headers=standard_ix_api_header(myAccount.token)) as session:
            put_tasks = []

            async for put_data in create_put_data(myAccount.userID, standard_blocks, job_status, siteID_list):
                put_tasks.append(set_standard_blocks(session, 'https://api01.indexexchange.com/api/tasks', put_data))
            # now execute them all at once
            results = await asyncio.gather(*put_tasks)
            return results


    async def set_standard_blocks(session, url, put_data):
        async with session.put(url, json=put_data) as response:
            if response.status == 202:
                print('The requested {} is succesfully queued'.format(put_data['task']))
            else:
                data = await response.text()
                print("set_siteID_blocks_service job failed")
                print(data)

    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(batch_requests())
    finally:
        loop.close()


# This function performs siteID Category updates for a list of siteIDs
# and a given AppAccount instance
def update_siteID_category_service(userID, siteIDs, categoryID):
    """
    This function updates a given Index Exchange AppAccount siteID(s)
    category. 
    These catagories can be found within the Viper2 database
    inside of the 'categories' table
    """
    if not isinstance(siteIDs, list):
        raise TypeError("Update_siteID_category_service(): The siteIDs argument must be type list")

    if not (isinstance(categoryID, int) and isinstance(userID, int)): 
        raise TypeError("Update_siteID_category_service(): The categoryID and userID arguments must be type int")
        
    API = AppAccount(userID)

    # This block verifies all siteID(s) passed belong to the given AppAccount
    siteID_checklist = [siteID['siteID'] for siteID in API.get_siteIDs_service(siteIDs)]
    if len(siteID_checklist) != len(siteIDs):
        error_value = [siteID for siteID in siteIDs if siteID not in siteID_checklist]
        raise RuntimeError("ERROR -- {} does NOT own siteID {}".format(API.userID, error_value[0]))


    async def create_patch_data(API, siteIDs, categoryID):
        for siteID in siteIDs:
            yield {
                "siteID": siteID,
                "siteTagCategory": categoryID,
                "userID": API.userID
            }


    async def batch_requests():
        async with aiohttp.ClientSession(headers=standard_ix_api_header(API.token)) as session:
            patch_tasks = []

            async for patch_data in create_patch_data(API, siteIDs, categoryID):
                patch_tasks.append(update_siteID(session, API, "https://api01.indexexchange.com/api/publishers/sites", patch_data))
            # now execute them all at once
            results = await asyncio.gather(*patch_tasks)
            return results




    async def update_siteID(session, API, url, patch_data):
        async with  session.patch(url, json=patch_data) as response:
            if response.status == 200:
                print("updated siteID {} to categoryID: {}".format(patch_data['siteID'], patch_data['siteTagCategory']))
                return patch_data["siteID"]
            else:
                data = await response.text()
                print("{} failed to update category".format(patch_data['siteID']))
                print(data)



    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(batch_requests())
    finally:
        loop.close()

    return results


# This function deletes AppAccount siteID(s)
def delete_siteIDs_service(userID, siteIDs):
    """
    This function deletes AppAccount siteID(s)
    The siteIDs argument must be passed in the form of a list/array
    """
    if not isinstance(userID, int):
        raise TypeError('Delete_siteIDs_service(): the userID argument must be of type int')

    API = AppAccount(userID)

    async def create_delete_data(API, siteIDs):
        for siteID in siteIDs:
            yield {
                "userID": API.userID,
                "siteID": siteID
            }

    async def batch_requests():
        async with aiohttp.ClientSession(headers=standard_ix_api_header(API.token)) as session:
            delete_tasks = []

            async for delete_data in create_delete_data(API, siteIDs):
                delete_tasks.append(delete_siteIDs(session, API, "https://api01.indexexchange.com/api/publishers/sites?userID={}&siteID={}", delete_data))
            # now execute them all at once
            results = await asyncio.gather(*delete_tasks)
            return results


    async def delete_siteIDs(session, API, url, request_body):
        async with session.delete(url.format(request_body['userID'], request_body['siteID']), json=request_body) as response:
            if response.status != 202:
                data = await response.text()
                print("Failed to delete siteID: {}".format(request_body['siteID']))
                print(data)
                return "FAILED TO DELETE SiteID: {}".format(request_body['siteID'])
            else:
                print('siteID {} has been deleted'.format(request_body['siteID']))
                return request_body['siteID']

    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(batch_requests())
    finally:
        loop.close()

    return results


# This function clones siteIDs for a given publisher Account
def clone_siteIDs_service(userID, base_siteID, excel_template):
    """
    This function clones siteIDs from a base_siteID. The ui_session_cookies
    argument are the cookies generated from a session in the Index Exchange
    Application
    """
    if not (isinstance(userID, int) and isinstance(base_siteID, int)):
        raise TypeError('clone_siteIDs_service(): The userID and base_siteID arguments must be of type int')


    # Verifying base_siteID ownership
    Database = Viper2()
    siteID_ownership = Database.get_account_siteIDs(userID, [base_siteID])
    if not siteID_ownership:
        raise RuntimeError("The account {} does NOT own siteID {}".format(userID, base_siteID))

    API = AppAccount(userID)
    account_details = API.get_account_info_service()
    validated_template = siteID_cloning_template_validator(excel_template)

    ui_session_cookies = get_ui_session_cookies()
    siteID_names = [siteID_name for siteID_name in validated_template['SiteID Name(s)']]

    return clone_siteIDs(userID, base_siteID, siteID_names, account_details, ui_session_cookies)

# This function clones siteIDs for a given publisher Account
def API_clone_siteID_service(userID, base_siteID, siteID_names):
    """
    This function clones siteIDs via the tropicalFantasy API endpoint
    """

    # Verifying base_siteID ownership
    Database = Viper2()
    siteID_ownership = Database.get_account_siteIDs(userID, [base_siteID])
    if not siteID_ownership:
        raise RuntimeError("The account {} does NOT own siteID {}".format(userID, base_siteID))

    # Validating siteID name types
    print(siteID_names)
    if not all(isinstance(siteID_name, str) for siteID_name in siteID_names):
        raise TypeError("All elements of the siteID_names list argument must be of type str")

    API = AppAccount(userID)
    account_details = API.get_account_info_service()
    ui_session_cookies = get_ui_session_cookies()

    return clone_siteIDs(userID, base_siteID, siteID_names, account_details, ui_session_cookies)


# This is general function for cloning siteIDs in the Index Exchange AppAccount
def clone_siteIDs(userID, base_siteID, siteID_names, account_details, ui_session_cookies):

    async def create_post_data(userID, base_siteID, siteID_names, account_email):
        for siteID_name in siteID_names:
            yield {
                "id": userID,
                "emailAddress": account_email,
                "siteID": base_siteID,
                "performClone": 1,
                "allowCloneSite": 1,
                "cloneSite": base_siteID,
                "cloneSiteName": siteID_name,
                "positionID": 1
            }


    async def batch_requests():
        async with aiohttp.ClientSession(headers={'content-Type': 'application/x-www-form-urlencoded'}, cookies=ui_session_cookies) as session:
            post_tasks = []

            async for post_data in create_post_data(userID, base_siteID, siteID_names, account_details['emailAddress']):
                post_tasks.append(clone_siteIDs(session, "https://system.indexexchange.com/cgi-bin/publisher/Accounts/publisherOptions.mcml", post_data))
            # now execute them all at once
            results = await asyncio.gather(*post_tasks)
            return results




    async def clone_siteIDs(session, url, post_data):
        async with  session.post(url, data=post_data) as response:
            for resp in response.history:
                if resp.status == 302:
                    regex = 'clonedSiteID=\d{6}'
                    siteID = re.findall(regex, str(resp.text))[0].split('=')[1]
                    print("created siteID {}: {}".format(post_data['cloneSiteName'], siteID))
                    return (post_data['cloneSiteName'], siteID)
                    
                else:
                    print("failed to obtain cloning redirect")
                    print("failed to create {}".format(post_data['cloneSiteName']))
                    return (post_data['cloneSiteName'], "Failed to Clone")
                    



    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(batch_requests())
    finally:
        loop.close()   
    
    return results