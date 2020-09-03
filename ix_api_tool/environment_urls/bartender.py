"""ix_api_tool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api_services import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tropicalFantasy', views.home_page, name='home'),
    path('tropicalFantasy/generatePlaceholder', views.placeholder_generator_view, name='gen_placeholder'),
    path('tropicalFantasy/customLibraryGenerator', views.custom_library_generator, name='gen_customLibrary'),
    path('tropicalFantasy/customLibraryTemplate', views.custom_library_template, name='customLibrary_template'),
    path('tropicalFantasy/addRemoveHtSlots', views.add_or_remove_htSlots, name='add_or_remove_htSlots'),
    path('tropicalFantasy/addRemoveHtSlotsTemplate', views.add_or_remove_htSlot_template, name='add_or_remove_htSlot_template'),
    path('tropicalFantasy/miniMassLauncher', views.mini_massLauncher, name='mass-launcher'),
    path('tropicalFantasy/copyLibrary', views.copy_library, name='copy-library'),
    path('tropicalFantasy/setStandardBlocks', views.set_standard_siteID_blocks, name='set_standard_blocks'),
    path('tropicalFantasy/updateSiteCategories', views.update_siteID_categories, name='update_site_categories'),
    path('tropicalFantasy/cloneSiteIDs', views.clone_siteIDs, name='clone_siteIDs'),
    path('tropicalFantasy/cloneSiteIDsTemplate', views.clone_siteID_template, name='clone_siteIDs_template'),
    path('tropicalFantasy/deleteSiteIDs', views.delete_siteIDs, name='delete_siteIDs'),

    # API urls

    path('tropicalFantasy/api/miniMassLauncher', views.API_mini_massLauncher),
    path('tropicalFantasy/api/setStandardBlocks',views.API_setStandard_siteID_blocks),
    path('tropicalFantasy/api/copyLibrary',views.API_copy_library),
    path('tropicalFantasy/api/generatePlaceHolder',views.API_generate_placeholder),
    path('tropicalFantasy/api/cloneSiteIDs',views.API_clone_siteIDs),
]
