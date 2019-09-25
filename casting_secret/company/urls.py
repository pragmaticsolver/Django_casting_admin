from django.conf.urls import url

from casting_secret.company.api import CompanyView

company_url = [
    url(r'^profile/(?P<slug>[-\w]+)/companies$',
        CompanyView.as_view({'get': 'get_profile_companies', 'post': 'create_new_company'}),
        name='company'),
    url(r'^companies/(?P<slug>[-\w]+)$',
        CompanyView.as_view({'get': 'get', 'patch': 'update_company', 'delete': 'delete'}),
        name='company_profile'),
    url(r'^company/(?P<slug>[-\w]+)/cover$', CompanyView.as_view({'patch': 'upload_cover'}),
        name='company_upload_cover'),
    url(r'^company/(?P<slug>[-\w]+)/avatar$', CompanyView.as_view({'patch': 'upload_avatar'}),
        name='company_upload_avatar'),
    url(r'^companies/(?P<slug>[-\w]+)/switch$', CompanyView.as_view({'post': 'switch_to_company'}),
        name='switch_to_company'),
    url(r'^companies/(?P<slug>[-\w]+)/follow$', CompanyView.as_view({'post': 'follow_company'}), name='company-follow'),
    url(r'^companies/(?P<slug>[-\w]+)/un-follow$', CompanyView.as_view({'post': 'unfollow_company'}),
        name='n-company-follow'),
    url(r'^search/companies/follow$', CompanyView.as_view({'get': 'get_loggedin_follow_company'}),
        name='get_loggedin_follow_company-follow'),
    url(r'^search/companies/own$', CompanyView.as_view({'get': 'get_my_own_company'}),
        name='get_my_own_company'),
]
