import re
import json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import (HttpResponse,
                         JsonResponse)
from django.shortcuts import render
from .services import (library_services, 
                       siteID_services)
from .forms import (PlaceHolderGeneratorForm,
                    CustomLibraryGeneratorForm,
                    AddOrRemoveSlotForm,
                    CopyLibraryForm,
                    StandardBlockForm,
                    UpdateSiteCategoriesForm,
                    MiniMassLaunchForm,
                    CloneSiteIDForm,
                    DeleteSiteIDForm,)

# Setting a global reference to the template used in all views
TEMPLATE_G = 'api_services/index.html'

def home_page(request):
    if "GET" == request.method:
        return render(request, TEMPLATE_G)


def placeholder_generator_view(request):
    form = PlaceHolderGeneratorForm
    context = {}
    context['title'] = 'Placeholder Library Generator'
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)
    
    if "POST" == request.method:
        post_data = form(request.POST)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data

            # gathering all arguments for placeholder generator service
            Type = cleaned_data['Type']
            name = cleaned_data['Placeholder_name']
            siteID = int(cleaned_data['site_ID'])
            userID = int(cleaned_data['user_ID'])
            try:
                response = library_services.placeholder_wrapper_generator(userID, name, siteID, Type)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})
        
        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


@csrf_exempt
def API_generate_placeholder(request):

    if "POST" != request.method:
        return HttpResponse(status=405)
    
    try:
        body = json.loads(request.body)
        keys_to_check = {'userID': int, 'type': str, 'name': str, 'siteID': int}
        for key in keys_to_check:
            if key not in body:
                return JsonResponse({'ERROR': 'The request is missing the paramater "{}"'.format(key)}, safe=False)
            if not isinstance(body[key], keys_to_check[key]):
                return JsonResponse({'ERROR': 'The request paramater "{}" is an INVALID TYPE'.format(key)}, safe=False)

        userID = body['userID']
        lib_type = body['type']
        siteID = body['siteID']
        library_name = body['name']

        response = library_services.placeholder_wrapper_generator(userID, library_name, siteID, lib_type)
        return JsonResponse({'success': str(response)}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})


# This functions allows the user to download the customLibraryTemplate.xlsx file
def custom_library_template(request):
    with open('api_services/service_templates/customLibraryTemplate.xlsx', 'rb') as files:
        response = HttpResponse(files.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename=customLibraryTemplate.xlsx'
        return response


def custom_library_generator(request):
    form = CustomLibraryGeneratorForm
    context = {}
    template_url = 'customLibrary_template'
    context['title'] = 'Custom Library Generator'
    context['template'] = template_url
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)
    
    if "POST" == request.method:
        post_data = form(request.POST, request.FILES)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data
            
            # This block ensures that the file submitted is an 'xlsx' file
            template_file = cleaned_data['Template_file']
            if not template_file.name.endswith('.xlsx'):
                return JsonResponse({'error': 'The file submitted is not an excel file'})
            
            userID = int(cleaned_data['user_ID'])
            library_name = cleaned_data['library_name']
            base_siteID = int(cleaned_data['site_ID'])
            configID = int(cleaned_data['configID'])
            clone_flag = cleaned_data['clone_siteID']

            if clone_flag.lower() == 'yes':
                clone_flag = True
            else:
                clone_flag = False

            try:
                response = library_services.custom_library_generator(userID, library_name, base_siteID, template_file, configID, clone_flag)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})

        else:
            return JsonResponse({'error': 'The form submitted is invalid'})

def add_or_remove_htSlots(request):
    form = AddOrRemoveSlotForm
    context = {}
    template_url = 'add_or_remove_htSlot_template'
    context['title'] = 'Add or Remove Headertag Slots'
    context['template'] = template_url
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)
    
    if "POST" == request.method:
        post_data = form(request.POST, request.FILES)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data
            
            # This block ensures that the file submitted is an 'xlsx' file
            template_file = cleaned_data['Template_file']
            if not template_file.name.endswith('.xlsx'):
                return JsonResponse({'error': 'The file submitted is not an excel file'})
            
            delete_flag = cleaned_data['add_or_remove_slots']
            if delete_flag.lower() == 'delete':
                delete_flag = True
                userID = int(cleaned_data['user_ID'])
                configID = int(cleaned_data['configID'])
            else:
                delete_flag = False
                userID = int(cleaned_data['user_ID'])
                base_siteID = int(cleaned_data['site_ID'])
                configID = int(cleaned_data['configID'])
                clone_flag = cleaned_data['clone_siteID']
                if clone_flag.lower() == 'yes':
                    clone_flag = True
                else:
                    clone_flag = False

            try:
                if delete_flag == True:
                    response = library_services.remove_library_slot(userID, configID, template_file)
                else:
                    response = library_services.add_htSlots(userID, base_siteID, template_file, configID, clone_flag, delete_flag)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})

        else:
            return JsonResponse({'error': 'The form submitted is invalid'})



# This functions allows the user to download the add_remove_htSlot.xlsx file
def add_or_remove_htSlot_template(request):
    with open('api_services/service_templates/add_remove_htSlotTemplate.xlsx', 'rb') as files:
        response = HttpResponse(files.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename=addRemoveHtSlotTemplate.xlsx'
        return response


def copy_library(request):
    form = CopyLibraryForm
    context = {}
    context['title'] = 'Copy Headertag Libraries'
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)

    if "POST" == request.method:
        post_data = form(request.POST)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data
            
            # Gathering all arguments
            home_userID = int(cleaned_data['home_user_ID'])
            destination_userID = int(cleaned_data['destination_userID'])
            base_siteID = int(cleaned_data['site_ID'])
            configID = int(cleaned_data['configID'])
            library_name = str(cleaned_data['library_name'])

            try:
                response = library_services.copy_library(home_userID, destination_userID, base_siteID, configID, library_name)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})
            
        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


@csrf_exempt
def API_copy_library(request):

    if "POST" != request.method:
        return HttpResponse(status=405)
    
    try:
        body = json.loads(request.body)
        keys_to_check = {'userID': int, 'configID': int, 'dest_userID':int, 'dest_siteID': int, 'library_name': str}
        for key in keys_to_check:
            if key not in body:
                return JsonResponse({'ERROR': 'The request is missing the paramater "{}"'.format(key)}, safe=False)
            if not isinstance(body[key], keys_to_check[key]):
                return JsonResponse({'ERROR': 'The request paramater "{}" is an INVALID TYPE'.format(key)}, safe=False)

        userID = body['userID']
        configID = body['configID']
        dest_userID = body['dest_userID']
        dest_siteID = body['dest_siteID']
        library_name = body['library_name']

        response = library_services.copy_library(userID, dest_userID, dest_siteID, configID, library_name)
        return JsonResponse({'success': str(response)}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})

def mini_massLauncher(request):
    form = MiniMassLaunchForm
    context = {}
    context['title'] = 'Mini Mass-Launcher'
    context['form'] = form
    
    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)

    if "POST" == request.method:
        post_data = form(request.POST)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data
            
            # Buildout service logic here
            userID = int(cleaned_data['user_ID'])
            launch_type = cleaned_data['job_status']

            try:
                response = library_services.mini_mass_launch(userID, launch_type)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})
            
        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


@csrf_exempt
def API_mini_massLauncher(request):
    
    if "POST" != request.method:
        return HttpResponse(status=405)
    
    try:
        body = json.loads(request.body)
        keys_to_check = {'userID': int, 'launch_type': str}
        for key in keys_to_check:
            if key not in body:
                return JsonResponse({'ERROR': 'The request is missing the paramater "{}"'.format(key)}, safe=False)
            if not isinstance(body[key], keys_to_check[key]):
                return JsonResponse({'ERROR': 'The request paramater "{}" is an INVALID TYPE'.format(key)}, safe=False)

        userID = body['userID']
        launch_type = body['launch_type']

        response = library_services.mini_mass_launch(userID, launch_type)
        return JsonResponse({'success': str(response)}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})


def set_standard_siteID_blocks(request):
    form = StandardBlockForm
    context = {}
    context['title'] = 'Standard Blocking Service'
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)

    if "POST" == request.method:
        post_data = form(request.POST)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data

            # gathering all arguments for standard blocking service
            userID = int(cleaned_data['user_ID'])
            siteIDs = cleaned_data['site_IDs']
            job_status = cleaned_data['job_status']

            # This block extracts all 6 digit values from the siteIDs
            # provided and sets them into a list
            regex = "\d{6}"
            siteID_matches = re.findall(regex, siteIDs)
            siteID_list = [int(ID) for ID in siteID_matches]

            # Setting the job_status to its correlating integer value
            if job_status == 'set blocks':
                block_service = 1
            else:
                block_service = 0
            try:
                siteID_services.set_standard_blocks(userID, siteID_list, block_service)
                response = 'The following siteIDs have been updated: {}'.format(siteID_list)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})
               
        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


@csrf_exempt
def API_setStandard_siteID_blocks(request):
    
    if "POST" != request.method:
        return HttpResponse(status=405)
    
    try:
        body = json.loads(request.body)
        keys_to_check = {'userID': int, 'siteIDs': list, 'job_type': int}
        for key in keys_to_check:
            if key not in body:
                return JsonResponse({'ERROR': 'The request is missing the paramater "{}"'.format(key)}, safe=False)
            if not isinstance(body[key], keys_to_check[key]):
                return JsonResponse({'ERROR': 'The request paramater "{}" is an INVALID TYPE'.format(key)}, safe=False)

        userID = body['userID']
        siteIDs = body['siteIDs']
        job_type = body['job_type']

        siteID_services.set_standard_blocks(userID, siteIDs, job_type)
        response = 'The following siteIDs have been updated: {}'.format(siteIDs)
        return JsonResponse({'Success': response}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})



def update_siteID_categories(request):
    form = UpdateSiteCategoriesForm
    context = {}
    context['title'] = 'Update SiteID(s) Category'
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)

    if "POST" == request.method:
        post_data = form(request.POST)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data

            # gathering all arguments for siteID category update
            userID = int(cleaned_data['user_ID'])
            categoryID = int(cleaned_data['category'])
            siteIDs = cleaned_data['site_IDs']

            # This block extracts all 6 digit values from the siteIDs
            # provided and sets them into a list
            regex = "\d{6}"
            siteID_matches = re.findall(regex, siteIDs)
            siteID_list = [int(ID) for ID in siteID_matches]

            try:
                response = siteID_services.update_siteID_category_service(userID, siteID_list, categoryID)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})

        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


def delete_siteIDs(request):
    form = DeleteSiteIDForm
    context = {}
    context['title'] = 'Delete SiteIDs'
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)

    if "POST" == request.method:
        post_data = form(request.POST)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data

            # Gathering all arguments for siteID Deletion
            userID = int(cleaned_data['user_ID'])
            siteIDs = cleaned_data['site_IDs']

            # This block extracts all 6 digit values from the siteIDs
            # provided and sets them into a list
            regex = "\d{6}"
            siteID_matches = re.findall(regex, siteIDs)
            siteID_list = [int(ID) for ID in siteID_matches]

            try:
                response = siteID_services.delete_siteIDs_service(userID, siteID_list)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})
        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


# This functions allows the user to download the clone_siteIDs_template.xlsx file
def clone_siteID_template(request):
    with open('api_services/service_templates/cloneSiteIDTemplate.xlsx', 'rb') as files:
        response = HttpResponse(files.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename=cloneSiteIDTemplate.xlsx'
        return response


def clone_siteIDs(request):
    form = CloneSiteIDForm
    context = {}
    template_url = 'clone_siteIDs_template'
    context['template'] = template_url
    context['title'] = 'SiteID Cloner'
    context['form'] = form

    if "GET" == request.method:
        return render(request, TEMPLATE_G, context)

    if "POST" == request.method:
        post_data = form(request.POST, request.FILES)
        if post_data.is_valid():
            cleaned_data = post_data.cleaned_data

            # Gathering all arguments for siteID cloning
            # This block ensures that the file submitted is an 'xlsx' file
            template_file = cleaned_data['Template_file']
            if not template_file.name.endswith('.xlsx'):
                return JsonResponse({'error': 'The file submitted is not an excel file'})

            userID = int(cleaned_data['user_ID'])
            base_siteID = int(cleaned_data['base_siteID'])

            try:
                response = siteID_services.clone_siteIDs_service(userID, base_siteID, template_file)
                return JsonResponse({'success': response})
            except Exception as error:
                return JsonResponse({'error': str(error)})
        else:
            return JsonResponse({'error': 'The form submitted is invalid'})


@csrf_exempt
def API_clone_siteIDs(request):
    
    if "POST" != request.method:
        return HttpResponse(status=405)
    
    try:
        body = json.loads(request.body)
        keys_to_check = {'userID': int, 'siteID_names': list, 'base_siteID': int}
        for key in keys_to_check:
            if key not in body:
                return JsonResponse({'ERROR': 'The request is missing the paramater "{}"'.format(key)}, safe=False)
            if not isinstance(body[key], keys_to_check[key]):
                return JsonResponse({'ERROR': 'The request paramater "{}" is an INVALID TYPE'.format(key)}, safe=False)

        userID = body['userID']
        siteID_names = body['siteID_names']
        base_siteID = body['base_siteID']

        response = siteID_services.API_clone_siteID_service(userID, base_siteID, siteID_names)
        return JsonResponse({'Success': response}, safe=False)

    except Exception as error:
        return JsonResponse({'ERROR': str(error)})