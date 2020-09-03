from ..classes.ui_service import AppAccount
from ..classes.viper2 import Viper2
from ..utilities.utility_function import (load_json, 
                                          template_validator,
                                          delete_htSlots_template_validator,
                                          standard_ix_api_header,
                                          get_ui_session_cookies)
import random
import asyncio
import aiohttp
import json
import re

# This function generates a placeholder library for the custom or auto libray from 
# a json file template.
def placeholder_wrapper_generator(userID, placeholder_name, siteID, wrapper_type):
    """
    This function generates either a placeholder auto library or custom/universal library
    """
    if not (isinstance(userID, int) and isinstance(siteID, int)):
        raise TypeError("placeholder_wrapper_generator() error: The userID and siteID arguments must be an integer")
    if not (isinstance(placeholder_name, str) and isinstance(wrapper_type, str)):
        raise TypeError("placeholder_wrapper_generator() error: The placeholder_name and wrapper_type argument must be a string")
    if 'placeholder' in placeholder_name.lower():
        raise RuntimeError("Please strip 'placeholder' from the library name as it will be appended by default")
    if wrapper_type != 'auto' and wrapper_type != 'custom':
        raise ValueError('placeholder_wrapper_generator() error: The wrapper_type argument must be "auto" or "custom"')

    # initialising the AppAccount class
    myAccount = AppAccount(userID)

    # This block determines what placeholder wrapper file will be loaded
    # depending on the "wrapper_type" argument passed
    if __name__ == "__main__":
        if wrapper_type == "auto":
            with open('placeholder_auto_wrapper.json', 'r') as files:
                placeholder_wrapper = json.load(files)
        elif wrapper_type == "custom":
            with open('placeholder_custom_wrapper.json', 'r') as files:
                placeholder_wrapper = json.load(files)
    else:
        if wrapper_type == "auto":
            with open('api_services/json_files/placeholder_auto_wrapper.json', 'r') as files:
                placeholder_wrapper = json.load(files)
        elif wrapper_type == "custom":
            with open('api_services/json_files/placeholder_custom_wrapper.json', 'r') as files:
                placeholder_wrapper = json.load(files)
    
    # Parsing through the wrapper object to set the appropriate placeholder settings
    placeholder_wrapper['name'] = "Placeholder - {}".format(placeholder_name)
    placeholder_wrapper['userID'] = myAccount.userID
    placeholder_wrapper['partners']['INDX']['slots'][0]['siteID'] = siteID
    
    myAccount.update_wrappers_service(placeholder_wrapper)
    success = "Placeholder - {} was generated succesfully for Account: {}".format(placeholder_name, userID)
    return success

# This function generates a custom/universal library based on the excel template provided.
# Any library specified will be overwritten
def custom_library_generator(userID, library_name, base_siteID, excel_template, configID, clone_flag):
    """
    This function generates a custom library with a predetermined HT Slot configuration
    based on the excel_templace passed
    """
    headings = load_json("api_services/json_files/customLib_template_headings.json")["headings"]
    supported_sizes = load_json("api_services/json_files/ix_supported_sizes.json")["supported_sizes"]

    if not (isinstance(userID, int) and isinstance(base_siteID, int) and isinstance(configID, int)):
        raise TypeError("custom_library_generator() error: The 'userID', 'siteID', and 'configID' arguments must be an integer")
    if not isinstance(clone_flag, bool):
        raise TypeError("custom_library_generator() error: The 'clone_flag' argument must be type boolean")
    if not isinstance(library_name, str):
        raise TypeError("custom_library_generator() error: The 'library_name' argument must be a string")
    
    # validating the excel_template
    try:
        validated_template = template_validator(excel_template, headings, supported_sizes)
    except Exception as error:
        raise error

    # initialising the AppAccount class
    myAccount = AppAccount(userID)
    # Verifying siteID ownership
    siteID_ownership = myAccount.get_siteIDs_service([base_siteID])
    if len(siteID_ownership) != len([base_siteID]):
        raise RuntimeError("The account {} does NOT own siteID {}".format(userID, base_siteID))
    # Verifying if the siteID is a headertag siteID or an Adtag siteID
    if siteID_ownership[0]['siteTypeID'] != 1:
        raise RuntimeError("The base siteID: {} is an Adtag siteID".format(base_siteID))


    # Pulling the desired wrapper to update if the wrapper is Custom and matches
    # the configID provided
    desired_wrapper = [library for library in myAccount.get_wrappers_service() if library['configID'] == configID and library['modeID'] == 4]
    if not desired_wrapper:
        raise RuntimeError("The configID provided is linked to a non-custom library or does NOT exist")
    else:
        desired_wrapper = desired_wrapper[0]

    # Setting the "configured" label and Emptying the desired wrappers htSlots/sizeRetargeting/ixSlot configurations
    desired_wrapper['name'] = 'Configured - ' + library_name
    desired_wrapper['htSlots'] = []
    desired_wrapper['sizeRetargeting'] = {}
    desired_wrapper['partners']['INDX']['slots'] = []

    display_tempID = 1
    slotID = 1
    video_tempID = ''

    # This function adds an additional slot to the custom library
    def add_custom_library_slot(wrapper_object, slot_name, device, position, sizes, Type, temperaryID):
        if device.lower() != 'desktop' and device.lower() != 'mobile':
            raise ValueError("The device argument must be 'desktop' or 'mobile")
        if position.lower() != 'atf' and position.lower() != 'btf':
            raise ValueError("The position argument must be 'atf' or 'btf'")
        if type(sizes) != list:
            raise TypeError("The sizes argument must be a list/array of string sizes Ex. ['300x250'] or ['300x250', '728x90']")
        if Type.upper() != 'BANNER' and Type.upper() != 'INSTREAM_VIDEO':
            raise ValueError("The Type argument must be 'BANNER' or 'INSTREAM_VIDEO'")
        # if type(temperaryID) != int:
        #     raise TypeError("The temperaryID argument must be type int")
        if wrapper_object['modeID'] != 4:
            raise RuntimeError("The wrapper_object passed is NOT a custom library")
        
        try:
            slot_sizes = [list(map(int, size.split('x'))) for size in sizes]
        except Exception as error:
            print("There was an issue processing the slot sizes. Please ensure they follow the format ['300x250'] or ['300x250', '728x90']")
            raise error

        # Video Slots can only contain ONE size. This check prevents Video slots of multiple
        # sizes from being added
        if Type == 'INSTREAM_VIDEO' and len(slot_sizes) > 1:
            raise RuntimeError("Video Slots can only contain ONE size. Please adjust the slot with sizes: {}".format(sizes))

        headerTag_slot = {
            'name': slot_name, 
            'device': device.lower(), 
            'position': position.lower(), 
            'sizeMapping': {'0x0': slot_sizes}, 
            'tmpID': str(temperaryID), 
            'type': Type.upper()
        }

        wrapper_object['htSlots'].append(headerTag_slot)
        if Type != 'INSTREAM_VIDEO':
            wrapper_object['sizeRetargeting'][temperaryID] = {}
        
        return wrapper_object

    # This function adds an IX slot siteID to the custom library
    def add_ix_slot(wrapper_object, tempID, slotID, siteID, width, height):
        if type(siteID) != int and type(width) != int and type(height != int):
            raise TypeError("add_ix_slot() error - The siteID, width, and height arguments must be type int")

        wrapper_object['partners']['INDX']['slots'].append({
            "htSlotID": str(tempID),
            "slotID": str(slotID),
            "siteID": siteID,
            "width": width,
            "height": height
        })

        wrapper_object['sizeRetargeting'][tempID] = {}
        return wrapper_object


    # Gathering the names and slotIDs for the necessary siteIDs
    def gather_siteID_names(validated_template, headings):
        siteID_names = {}
        creation_count = 1
        for index in range(len(validated_template['Slot Name'])):
            

            flex = ''
            #appending all entries from each row of the excel sheet to the wrapper's htSlot list to update
            name = validated_template[headings[0]][index]
            Type = validated_template[headings[1]][index].upper()
            position = validated_template[headings[2]][index].lower()
            size = validated_template[headings[3]][index]
            device = validated_template[headings[4]][index]

            if Type != "INSTREAM_VIDEO":
                if size.count('x') == 1:
                    flex = False
                elif size.count('x') >= 2:
                    flex = True

                if not flex:
                    siteID_names[creation_count] = '{} - {} - {} - {} - {}'.format(name, device, Type, position, size)
                    creation_count += 1
                else:
                    size_split = size.split(',')
                    for single_size in size_split:
                        siteID_names[creation_count] = '{} - {} - {} - {} - {}'.format(name, device, Type, position, single_size)
                        creation_count += 1

        return siteID_names

    # Clone siteIDs
    def clone_siteIDs(API, base_siteID, siteID_names, ui_session_cookies):
        """
        This function clones siteIDs from a base_siteID. The ui_session_cookies
        argument are the cookeis generated from a session in the Index Exchange
        Application
        """

        account_details = API.get_account_info_service()

        async def create_post_data(userID, base_siteID, siteID_names, account_email):
            for key, siteID_name in siteID_names.items():
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

                async for post_data in create_post_data(API.userID, base_siteID, siteID_names, account_details['emailAddress']):
                    post_tasks.append(clone_siteIDs(session, API, "https://system.indexexchange.com/cgi-bin/publisher/Accounts/publisherOptions.mcml", post_data))
                # now execute them all at once
                results = await asyncio.gather(*post_tasks)
                return results




        async def clone_siteIDs(session, API, url, post_data):
            async with  session.post(url, data=post_data) as response:
                for resp in response.history:
                    if resp.status == 302:
                        regex = 'clonedSiteID=\d{6}'
                        siteID = re.findall(regex, str(resp.text))[0].split('=')[1]
                        print("created siteID: {}".format(siteID))
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
        
        for key, siteID in zip(siteID_names, results):
            siteID_names[key] = int(siteID[1])
        return siteID_names


    # The pattern matching regex to find all sizes under the "Sizes" columb
    size_regex = '\d{1,4}x\d{1,4}'

    if clone_flag:
        siteID_names = gather_siteID_names(validated_template, headings)
        cookies = get_ui_session_cookies()
        slot_siteIDs = clone_siteIDs(myAccount, base_siteID, siteID_names, cookies)

    for index in range(len(validated_template[headings[0]])):
        #appending all entries from each row of the excel sheet to the wrapper's htSlot list to update
        name = validated_template[headings[0]][index]
        Type = validated_template[headings[1]][index].upper()
        position = validated_template[headings[2]][index].lower()
        sizes = re.findall(size_regex, validated_template[headings[3]][index])
        device = validated_template[headings[4]][index]

        if Type != 'INSTREAM_VIDEO':
            desired_wrapper = add_custom_library_slot(desired_wrapper, name, device, position, sizes, Type, display_tempID)
            try:
                slot_sizes = [list(map(int, size.split('x'))) for size in sizes]
            except Exception as error:
                print("There was an issue processing the slot sizes. Please ensure they follow the format ['300x250'] or ['300x250', '728x90']")
                raise error

            for size in slot_sizes:
                if clone_flag:
                    siteID = slot_siteIDs[slotID]
                else:
                    siteID = base_siteID

                add_ix_slot(desired_wrapper, display_tempID, slotID, siteID, size[0], size[1])
                slotID += 1

            display_tempID += 1
        else:
            video_tempID = 'Vid + {}'.format(random.randint(100000, 1000000))
            desired_wrapper = add_custom_library_slot(desired_wrapper, name, device, position, sizes, Type, video_tempID)

    try:
        myAccount.update_wrappers_service(desired_wrapper)
        success = '"{}" was updated succesfully'.format(desired_wrapper['name'])
        return success
        
    except Exception as error:
        # Should the library fail to update after cloning siteID(s), all siteID(s)
        # cloned will be deleted
        if clone_flag:
            created_siteIDs = [slot_siteIDs[key] for key in slot_siteIDs]
            from ..services.siteID_services import delete_siteIDs_service
            delete_siteIDs_service(myAccount.userID, created_siteIDs)
        raise error

# This function adds headertag slots to a desired library based on the template provided
def add_htSlots(userID, base_siteID, excel_template, configID, clone_flag, delete_flag):
    """
    This function adds headertag library slots to a given library based on the excel_template
    provided
    """
    if not (isinstance(userID, int) and isinstance(base_siteID, int) and isinstance(configID, int)):
        raise TypeError("add_or_remove_htSlots() error: The 'userID', 'siteID', and 'configID' arguments must be an integer")
    if not isinstance(clone_flag, bool):
        raise TypeError("add_or_remove_htSlots() error: The 'clone_flag' argument must be type boolean")


    # This function adds an additional slot to a custom library
    def add_library_slot(wrapper_object, slot_name, device, position, sizes, Type, temperaryID, mapping, targeting=None):
        """
        This function adds a headertag slot to a library

        wrapper_object = The entire front-end library configuration - type - (dictionary)
        slot_name = type - (str)
        device = Must be ("desktop" or "mobile") - type - (str)
        position = Must be ("atf" or "btf") - type - (str)
        Type = Must be ("INSTREAM_VIDEO" or "BANNER") - type - (str)
        sizes = Must be (Ex. ['300x250'] or ['300x250', '728x90']) - type - (list)
        temperaryID = Must be a number - type - (int)
        mapping = Must be ("None", "divId", "divIdRegExBySize", "adUnitPathRegEx", "targeting") - type - (str)
        targeting = The targeting of the desired mapping
        """

        if device.lower() != 'desktop' and device.lower() != 'mobile':
            raise ValueError("The device argument must be 'desktop' or 'mobile")
        if position.lower() != 'atf' and position.lower() != 'btf':
            raise ValueError("The position argument must be 'atf' or 'btf'")
        if type(sizes) != list:
            raise TypeError("The sizes argument must be a list/array of string sizes Ex. ['300x250'] or ['300x250', '728x90']")
        if Type.upper() != 'BANNER' and Type.upper() != 'INSTREAM_VIDEO':
            raise ValueError("The Type argument must be 'BANNER' or 'INSTREAM_VIDEO'")


        mapping_types = ["None", "divId", "divIdRegExBySize", "adUnitPathRegEx", "targeting"]
        if mapping not in mapping_types:
            raise RuntimeError("The mapping type must be one of the following: {}".format(mapping_types))

        if mapping != 'None' and wrapper_object['modeID'] == 4:
            raise RuntimeError("Custom libraries do not support mapping types. Please update the template sheet")

        try:
            slot_sizes = [list(map(int, size.split('x'))) for size in sizes]
        except Exception as error:
            print("There was an issue processing the slot sizes. Please ensure they follow the format ['300x250'] or ['300x250', '728x90']")
            raise error

        # Video Slots can only contain ONE size. This check prevents Video slots of multiple
        # sizes from being added
        if Type == 'INSTREAM_VIDEO' and len(slot_sizes) > 1:
            raise RuntimeError("Video Slots can only contain ONE size. Please adjust the slot with sizes: {}".format(sizes))

        headerTag_slot = {
            'name': slot_name, 
            'device': device.lower(), 
            'position': position.lower(), 
            'sizeMapping': {'0x0': slot_sizes}, 
            'tmpID': str(temperaryID), 
            'type': Type.upper()
        }

        if mapping != 'None' and targeting and wrapper_object['modeID'] != 4: 
            # The library can support multiple key-value targetings set in a list
            # This block formats the key-value targeting to be set in a list
            if mapping == 'targeting':
                split_targeting = targeting.split(',')
                list_targeting = [{target.split('=')[0].strip(): [target.split('=')[1].strip()]} for target in split_targeting]
                headerTag_slot[mapping] = list_targeting
            else:
                headerTag_slot[mapping] = targeting

        wrapper_object['htSlots'].append(headerTag_slot)
        if Type != 'INSTREAM_VIDEO':
            wrapper_object['sizeRetargeting'][temperaryID] = {}

        return wrapper_object

    
        
        if removed_slotID:
            # TODO Currently the delete function will only work if the headertag slot submitted
            # is not mapped OR ONLY mapped to index adapter slots. If it is mapped to any other
            # adapter it will not work

            # Removing all references to the slotID from the sizeRetargeting field
            wrapper_object['sizeRetargeting'] = {slotID: {} for slotID in wrapper_object['sizeRetargeting'] if slotID != removed_slotID}
            # Removing all Index siteIDs currently mapped to the slot
            wrapper_object['partners']['INDX']['slots'] = [ix_adapter_slot for ix_adapter_slot in wrapper_object['partners']['INDX']['slots'] if ix_adapter_slot['htSlotID'] != removed_slotID]

        return wrapper_object

    # This function adds an IX slot siteID to the custom library
    def add_ix_slot(wrapper_object, tempID, slotID, siteID, width, height):
        if type(siteID) != int and type(width) != int and type(height != int):
            raise TypeError("add_ix_slot() error - The siteID, width, and height arguments must be type int")

        wrapper_object['partners']['INDX']['slots'].append({
            "htSlotID": str(tempID),
            "slotID": str(slotID),
            "siteID": siteID,
            "width": width,
            "height": height
        })

        wrapper_object['sizeRetargeting'][tempID] = {}
        return wrapper_object

    # Gathering the names and slotIDs for the necessary siteIDs
    def gather_siteID_names(validated_template, headings):
        siteID_names = {}
        creation_count = 1
        for index in range(len(validated_template['Slot Name'])):
            

            flex = ''
            #appending all entries from each row of the excel sheet to the wrapper's htSlot list to update
            name = validated_template[headings[0]][index]
            Type = validated_template[headings[1]][index].upper()
            position = validated_template[headings[2]][index].lower()
            size = validated_template[headings[3]][index]
            device = validated_template[headings[4]][index]

            if Type != "INSTREAM_VIDEO":
                if size.count('x') == 1:
                    flex = False
                elif size.count('x') >= 2:
                    flex = True

                if not flex:
                    siteID_names[creation_count] = '{} - {} - {} - {} - {}'.format(name, device, Type, position, size)
                    creation_count += 1
                else:
                    size_split = size.split(',')
                    for single_size in size_split:
                        siteID_names[creation_count] = '{} - {} - {} - {} - {}'.format(name, device, Type, position, single_size)
                        creation_count += 1

        return siteID_names

    # Clone siteIDs
    def clone_siteIDs(API, base_siteID, siteID_names, ui_session_cookies):
        """
        This function clones siteIDs from a base_siteID. The ui_session_cookies
        argument are the cookeis generated from a session in the Index Exchange
        Application
        """

        account_details = API.get_account_info_service()

        async def create_post_data(userID, base_siteID, siteID_names, account_email):
            for key, siteID_name in siteID_names.items():
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

                async for post_data in create_post_data(API.userID, base_siteID, siteID_names, account_details['emailAddress']):
                    post_tasks.append(clone_siteIDs(session, API, "https://system.indexexchange.com/cgi-bin/publisher/Accounts/publisherOptions.mcml", post_data))
                # now execute them all at once
                results = await asyncio.gather(*post_tasks)
                return results




        async def clone_siteIDs(session, API, url, post_data):
            async with  session.post(url, data=post_data) as response:
                for resp in response.history:
                    if resp.status == 302:
                        regex = 'clonedSiteID=\d{6}'
                        siteID = re.findall(regex, str(resp.text))[0].split('=')[1]
                        print("created siteID: {}".format(siteID))
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
        
        for key, siteID in zip(siteID_names, results):
            siteID_names[key] = int(siteID[1])

        return siteID_names

    # Verifying if the desired library can support additional slots
    def validating_additional_slots(desired_wrapper, validated_template, headings):
        slot_counter = 0
        for sizes, name in zip(validated_template[headings[3]], validated_template[headings[0]]):
            slot_counter += len(re.findall('\d{1,4}x\d{1,4}', sizes))
            name_check = [slot for slot in desired_wrapper['htSlots'] if slot['name'].lower() == name.lower()]

            if name_check:
                raise RuntimeError('SlotName "{}" already exists in library {}'.format(name, desired_wrapper['name']))

        if 100 - len(desired_wrapper['partners']['INDX']['slots']) < slot_counter:
            raise RuntimeError("Too many slots to add for library: {} -- Please adjust it and try again".format(desired_wrapper['name']))



    headings = load_json("api_services/json_files/customLib_template_headings.json")["headings"]
    supported_sizes = load_json("api_services/json_files/ix_supported_sizes.json")["supported_sizes"]
    
    # validating the excel_template
    try:
        validated_template = template_validator(excel_template, headings, supported_sizes)
    except Exception as error:
        raise error

    # initialising the AppAccount class
    myAccount = AppAccount(userID)
    # Verifying siteID ownership
    siteID_ownership = myAccount.get_siteIDs_service([base_siteID])
    if len(siteID_ownership) != len([base_siteID]):
        raise RuntimeError("The account {} does NOT own siteID {}".format(userID, base_siteID))
    # Verifying if the siteID is a headertag siteID or an Adtag siteID
    if siteID_ownership[0]['siteTypeID'] != 1:
        raise RuntimeError("The base siteID: {} is an Adtag siteID".format(base_siteID))


    # Pulling the desired wrapper to update if the wrapper is Custom and matches
    # the configID provided
    desired_wrapper = [library for library in myAccount.get_wrappers_service() if library['configID'] == configID]
    if not desired_wrapper:
        raise RuntimeError("No Library in {} contain matching configID(s): {}".format(configID))
    
    desired_wrapper = desired_wrapper[0]
    validating_additional_slots(desired_wrapper, validated_template, headings)

    if clone_flag:
        siteID_names = gather_siteID_names(validated_template, headings)
        cookies = get_ui_session_cookies()
        slot_siteIDs = clone_siteIDs(myAccount, base_siteID, siteID_names, cookies)

    # This block determines the start point for the ix slotIDs
    # This is to ensure the code does not run into erros of prexisting slotIDs
    ix_slotID_integers = [int(slot['slotID']) for slot in desired_wrapper['partners']['INDX']['slots'] if slot['slotID'].isnumeric()]
    if ix_slotID_integers:
        ix_slotID = max(ix_slotID_integers) + 1
    else:
        ix_slotID = 1

    display_tempID = 1
    slotID = 1
    video_tempID = ''
    size_regex = '\d{1,4}x\d{1,4}'



    for index in range(len(validated_template[headings[0]])):

        #appending all entries from each row of the excel sheet to the wrapper's htSlot list to update
        name = validated_template[headings[0]][index]
        Type = validated_template[headings[1]][index].upper()
        position = validated_template[headings[2]][index].lower()
        sizes = re.findall(size_regex, validated_template[headings[3]][index])
        device = validated_template[headings[4]][index]
        mapping_label = validated_template.columns[5]
        mapping = validated_template[mapping_label][index]

        if Type != 'INSTREAM_VIDEO':
            if mapping_label != 'None':
                desired_wrapper = add_library_slot(desired_wrapper, name, device, position, sizes, Type, display_tempID, mapping_label, mapping)
            else:
                desired_wrapper = add_library_slot(desired_wrapper, name, device, position, sizes, Type, display_tempID, mapping_label)
            try:
                slot_sizes = [list(map(int, size.split('x'))) for size in sizes]
            except Exception as error:
                print("There was an issue processing the slot sizes. Please ensure they follow the format ['300x250'] or ['300x250', '728x90']")
                raise error

            for size in slot_sizes:
                if clone_flag:
                    siteID = slot_siteIDs[slotID]
                else:
                    siteID = base_siteID

                # creation_tempID_label = 'AddedSlot{}'.format(slotID)
                add_ix_slot(desired_wrapper, display_tempID, ix_slotID, siteID, size[0], size[1])
                slotID += 1
                ix_slotID += 1

            display_tempID += 1
        else:
            video_tempID = 'Vid + {}'.format(random.randint(100000, 1000000))
            if mapping_label != 'None':
                desired_wrapper = add_library_slot(desired_wrapper, name, device, position, sizes, Type, video_tempID, mapping_label, mapping)
            else:
                desired_wrapper = add_library_slot(desired_wrapper, name, device, position, sizes, Type, video_tempID, mapping_label, mapping)

    try:
        myAccount.update_wrappers_service(desired_wrapper)
        success = '"{}" was updated succesfully'.format(desired_wrapper['name'])
        return success

    except Exception as error:
        # Should the library fail to update after cloning siteID(s), all siteID(s)
        # cloned will be deleted
        if clone_flag:
            created_siteIDs = [slot_siteIDs[key] for key in slot_siteIDs]
            from ..services.siteID_services import delete_siteIDs_service
            delete_siteIDs_service(myAccount.userID, created_siteIDs)
        raise error

# This function copies headerbidding libraries
def copy_library(home_userID, destination_userID, base_siteID, configID, library_name):
    """
    This function clones headerbidding libraries to the same account
    or to a new AppAccount
    """
    if not (isinstance(home_userID, int) and isinstance(base_siteID, int) and isinstance(configID, int)):
        raise TypeError("copy_library() - The userID, base_siteID, and configID arguments must be type int")
    if not isinstance(library_name, str):
        raise TypeError("copy_library() - The library name argument must be of type str")

    myAccount = AppAccount(home_userID)
    library_list_flag = [library for library in myAccount.get_wrappers_service() if library['configID'] == configID]

    if not library_list_flag:
        raise RuntimeError("The configID:{} Does not correspond to any library in AppAccount: {}".format(configID, home_userID))
    library_to_copy = library_list_flag[0]

    # The following section adjusts the library object paramters to copy succesfully
    del library_to_copy['configID']

    # The htSlotID key inside of the htSlots list/array must be replaced with tmpID
    # when updating via the API
    for htSlot in library_to_copy['htSlots']:
        slotID = htSlot['htSlotID']
        del htSlot['htSlotID']
        htSlot['tmpID'] = slotID

    # The IX adapter slot(s) siteID(s) must be replaced since the new Account will
    # NOT own the current siteIDs set. If the library in question is being copied 
    # to the same AppAccount this will be avoided

    if library_to_copy['userID'] != destination_userID:
        library_to_copy['userID'] = destination_userID
        for ixSlot in library_to_copy['partners']['INDX']['slots']:
            ixSlot['siteID'] = base_siteID


    library_to_copy['name'] = library_name
    myAccount.update_wrappers_service(library_to_copy)
    return "Library: {} was succesfully copied to AppAccount: {}".format(configID, destination_userID)

# This function removes a htSlot from a desired library
def remove_library_slot(userID, configID, excel_template):
    """
    This function removes a headertag slot and all
    associated Index adapter slots

    The slot_name must exist in the library otherwise 
    the update will fail
    """
    if not (isinstance(userID, int) and isinstance(configID, int)):
        raise TypeError("remove_library_slot() - Error - the userID and configID arguments must be of type int")

    validated_template = delete_htSlots_template_validator(excel_template)
    myAccount = AppAccount(userID)
    desired_wrapper = [wrapper for wrapper in myAccount.get_wrappers_service() if wrapper['configID'] == configID]
    if not desired_wrapper:
        raise RuntimeError("AppAccount {} does not own any wrappers with a configID of: {}".format(userID, configID))

    desired_wrapper = desired_wrapper[0]
    htSlot_names = validated_template['Slot Name'].tolist()

    starting_htSlot_counter = len(desired_wrapper['htSlots'])
    updated_slots = []
    removed_slotIDs = []
    for slot in desired_wrapper['htSlots']:
        if slot['name'] not in htSlot_names:
            updated_slots.append(slot)
        else:
            removed_slotIDs.append(slot['htSlotID'])

    if removed_slotIDs:
        # TODO Currently the delete function will only work if the headertag slot submitted
        # is not mapped OR ONLY mapped to index adapter slots. If it is mapped to any other
        # adapter it will not work

        # Removing all references to the slotID from the sizeRetargeting field
        desired_wrapper['sizeRetargeting'] = {slotID: {} for slotID in desired_wrapper['sizeRetargeting'] if slotID not in removed_slotIDs}
        # Removing all Index siteIDs currently mapped to the slot
        desired_wrapper['partners']['INDX']['slots'] = [ix_adapter_slot for ix_adapter_slot in desired_wrapper['partners']['INDX']['slots'] if ix_adapter_slot['htSlotID'] not in removed_slotIDs]

    desired_wrapper['htSlots'] = updated_slots
    final_htSlot_counter = len(desired_wrapper['htSlots'])
    if starting_htSlot_counter == final_htSlot_counter:
        return "No Slots were deleted as library {} did not contain any matching htSlot names".format(desired_wrapper['name'])
    else:
        myAccount.update_wrappers_service(desired_wrapper)
        return "Remove htSlot(s) job succesful!"

# This function launched ALL libraries not locked in a given AppAccount
def mini_mass_launch(userID, launch_type):
    """
    This function launcheds all libraries that are not locked in a given
    AppAccount 
    """
    if not isinstance(userID, int):
        raise TypeError('mini_mass_launcher(): The userID argument must be of type int')
    if not isinstance(launch_type, str):
        raise TypeError('mini_mass_launcher(): The launch_type argument must be of type str')
    if launch_type != 'staging' and launch_type != 'production':
        raise ValueError('mini_mass_launcher(): The launch_type argument must be either "staging" or "production"')

    myAccount = AppAccount(userID)
    libraries = myAccount.get_wrappers_service()

    # initialising the Viper2 DB connection
    from ..classes.viper2 import Viper2
    Database = Viper2()

    # Gathering all locked libraries for checks
    locked_configIDs = Database.get_locked_libraries(userID)

    async def create_put_data(userID, wrapper_objects, launch_type):
        for library in wrapper_objects:
            if library['configID'] in locked_configIDs:
                continue
            else:
                yield {
                    "configID": library['configID'],
                    "buildTo": launch_type,
                    "userID": userID
                }


    async def mass_launch():
        async with aiohttp.ClientSession(headers=standard_ix_api_header(myAccount.token)) as session:
            put_tasks = []
            url = 'https://api01.indexexchange.com/api/headertag/wrapper/files'

            async for put_data in create_put_data(userID, libraries, launch_type):
                put_tasks.append(do_put_request(session, url, put_data))

            results = await asyncio.gather(*put_tasks)
            return results


    async def do_put_request(session, url, put_data):
        async with  session.put(url, json=put_data) as response:
            if response.status == 200:
                data = await response.json()
                print("{} has been launched to {}".format(put_data['configID'], put_data['buildTo']))
                return data
            else:
                data = await response.text()
                print("ERROR - Failed to launch {}".format(put_data['configID']))
                print(data)


    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(mass_launch())
    finally:
        loop.close()

    wrappersIDs_launched = [response['data']['configID'] for response in results]
    library_names = [library['name'] for library in libraries if library['configID'] in wrappersIDs_launched]
    return library_names