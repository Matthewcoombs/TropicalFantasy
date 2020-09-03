from django import forms
from .utilities.utility_function import load_json

class PlaceHolderGeneratorForm(forms.Form):
    WRAPPER_TYPE = (
        ('auto', 'Auto Library'),
        ('custom', 'Custom Library')
    )
    Type = forms.ChoiceField(choices = WRAPPER_TYPE)
    Placeholder_name = forms.CharField(label="Placeholder Name",max_length=100)
    site_ID = forms.CharField(label="siteID", max_length=6)
    user_ID = forms.CharField(label="userID", max_length=6)

class CustomLibraryGeneratorForm(forms.Form):
    CLONE_SITEIDS = (
        ('no', 'No'),
        ('yes', 'Yes')
    )
    user_ID = forms.CharField(label="userID",max_length=6)
    library_name = forms.CharField(label="Library name",max_length=100)
    configID = forms.CharField(label="Configuration ID",max_length=100)
    site_ID = forms.CharField(label="Base SiteID",max_length=6)
    clone_siteID = forms.ChoiceField(label="Clone SiteIDs?", choices=CLONE_SITEIDS)
    Template_file = forms.FileField()

class AddOrRemoveSlotForm(forms.Form):
    CLONE_SITEIDS = (
        ('no', 'No'),
        ('yes', 'Yes')
    )
    ADD_REMOVE = (
        ('add', 'Add'),
        ('delete', 'Delete')
    )
    add_or_remove_slots = forms.ChoiceField(label="Job Type", choices=ADD_REMOVE)
    user_ID = forms.CharField(label="userID",max_length=6)
    configID = forms.CharField(label="Configuration ID",max_length=100)
    site_ID = forms.CharField(label="Base SiteID",max_length=6, required=False)
    clone_siteID = forms.ChoiceField(label="Clone SiteIDs?", choices=CLONE_SITEIDS, required=False)
    Template_file = forms.FileField()

class CopyLibraryForm(forms.Form):
    home_user_ID = forms.CharField(label="UserID",max_length=6)
    configID = forms.CharField(label="ConfigurationID",max_length=100)
    destination_userID = forms.CharField(label="Destination AppAccount UserID",max_length=6)
    site_ID = forms.CharField(label="Destination AppAccount siteID",max_length=6, required=False)
    library_name = forms.CharField(label="Library name",max_length=100)

class MiniMassLaunchForm(forms.Form):
    LAUNCH_TYPE = (
        ('staging', 'Staging'),
        ('production', 'Production')
    )

    user_ID = forms.CharField(label="userID",max_length=6)
    job_status = forms.ChoiceField(label="Launch Type", choices=LAUNCH_TYPE)

class StandardBlockForm(forms.Form):
    BLOCK_TYPE = (
        ('set blocks', 'Set Blocks'),
        ('remove blocks', 'Remove Blocks')
    )

    user_ID = forms.CharField(label="userID", max_length=6)
    job_status = forms.ChoiceField(label="Job",choices=BLOCK_TYPE)
    site_IDs =  forms.CharField(label="siteIDs", widget=forms.Textarea(attrs={}))

class UpdateSiteCategoriesForm(forms.Form):
    CATEGORIES = (
        (2, 'Tech & Gaming > Tech News'),
        (4, 'Education & Careers > Fine Arts & Photography'),
        (6, 'Education & Careers > Literature'),
        (9, 'Autos > General Interest'),
        (10, 'Autos > Buying Guides'),
        (16, 'Money & Investing > Personal Finance'),
        (17, 'Education & Careers > Careers & Jobs'),
        (18, 'B-to-B > Business News'),
        (25, 'Tech & Gaming > Registrars'),
        (26, 'Tech & Gaming > Tech Resources'),
        (28, 'Tech & Gaming > Website Development'),
        (30, 'Community & Culture > Social Expressions'),
        (31, 'Glamour > Celebrities'),
        (32, 'Casual Games > Games & Puzzles'),
        (34, 'Community & Culture > Humor & Entertainment'),
        (35, 'Movies & Television > Movies'),
        (37, 'Movies & Television > Television'),
        (39, 'Tech & Gaming > Console Games'),
        (41, 'Family & Parenting > General'),
        (42, 'Family & Parenting > Parenting'),
        (43, 'Family & Parenting > Wedding'),
        (46, 'B-to-B > Business Resources'),
        (47, 'Money & Investing > Investing'),
        (49, 'Home > Real Estate'),
        (52, 'Health & Wellness > Nutrition'),
        (53, 'Glamour > Beauty'),
        (54, 'Health & Wellness > Weight Loss'),
        (56, 'Health & Wellness > Reference'),
        (57, 'Glamour > Women'),
        (59, 'Food > Cooking & Baking'),
        (60, 'Leisure > Gardening'),
        (61, 'Home > General'),
        (62, 'Home > Home Improvement'),
        (63, 'Home > Pets'),
        (65, 'Music & Radio > Amateur Artists'),
        (66, 'Music & Radio > Broadcasts'),
        (69, 'Music & Radio > General'),
        (70, 'Music & Radio > Songs & Videos'),
        (73, 'News & Portals > Newspapers'),
        (74, 'News & Portals > News & Commentary'),
        (76, 'News & Portals > Weather'),
        (79, 'Leisure > Hobbies'),
        (80, 'Leisure > Astrology'),
        (82, 'Casual Games > Sweepstakes'),
        (83, 'Community & Culture > Photo Sharing'),
        (84, 'Food > Entertaining'),
        (86, 'Community & Culture > General'),
        (87, 'Leisure > Outdoors'),
        (89, 'Education & Careers > Science & Technology'),
        (90, 'Education & Careers > History & Reference'),
        (95, 'Shopping > Auctions & Classifieds'),
        (100, 'Shopping > Free Stuff'),
        (102, 'Shopping > Business Directories'),
        (106, 'Shopping > Shopping & Comparison'),
        (108, 'Sports > Baseball'),
        (109, 'Sports > Basketball'),
        (110, 'Sports > Boxing'),
        (111, 'Health & Wellness > Fitness'),
        (112, 'Sports > Action Sports'),
        (113, 'Sports > Football'),
        (114, 'Sports > News & Scores'),
        (115, 'Sports > Golf'),
        (116, 'Sports > Hockey'),
        (121, 'Sports > Soccer'),
        (122, 'Sports > Tennis'),
        (124, 'Sports > Wrestling'),
        (127, 'Travel > Transportation'),
        (130, 'Travel > Destinations'),
        (131, 'Travel > General'),
        (149, 'Music & Radio > Lyrics'),
        (150, 'Music & Radio > Tablature'),
        (152, 'News & Portals > Television Stations'),
        (153, 'News & Portals > Portals'),
        (154, 'News & Portals > International News'),
        (156, 'Leisure > Greeting Cards'),
        (157, 'Education & Careers > K-12'),
        (158, 'Leisure > Poetry'),
        (163, 'Education & Careers > Facts & Trivia'),
        (164, 'News & Portals > Comic Strips'),
        (168, 'Community & Culture > Social Networking')
    )

    user_ID = forms.CharField(label="userID", max_length=6)
    category = forms.ChoiceField(choices=CATEGORIES)
    site_IDs =  forms.CharField(label="siteIDs", widget=forms.Textarea(attrs={}))

class CloneSiteIDForm(forms.Form):
    user_ID = forms.CharField(label="userID",max_length=6)
    base_siteID = forms.CharField(label="Base SiteID",max_length=6)
    Template_file = forms.FileField(label="Cloning Template")

class DeleteSiteIDForm(forms.Form):
    user_ID = forms.CharField(label="userID",max_length=6)
    site_IDs =  forms.CharField(label="siteIDs", widget=forms.Textarea(attrs={}))