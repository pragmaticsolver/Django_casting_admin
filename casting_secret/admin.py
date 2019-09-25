from django.contrib import admin

from casting_secret.models import ActivityAttachment, Albums, Company
from casting_secret.models.models import TalentCategories
from casting_secret.models.profile_models import UsersProfile, AgeRangeLookUp, HeightRangeLookUp, WeightRangeLookUp, \
    BuildLookUp, HairLookUp, EyesLookUp, EthnicitiesLookUp, HobbiesLookUp, ProfileSettings

# admin.site.register(Job)
admin.site.register(Albums)
admin.site.register(Company)
admin.site.register(EyesLookUp)
admin.site.register(HairLookUp)
admin.site.register(BuildLookUp)
admin.site.register(UsersProfile)
admin.site.register(HobbiesLookUp)
admin.site.register(AgeRangeLookUp)
admin.site.register(ProfileSettings)
admin.site.register(TalentCategories)
admin.site.register(HeightRangeLookUp)
admin.site.register(WeightRangeLookUp)
admin.site.register(EthnicitiesLookUp)
admin.site.register(ActivityAttachment)
