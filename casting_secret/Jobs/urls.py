from django.conf.urls import url

from casting_secret.Jobs.api import JobView, RandomJobs

job_url_patterns = [
    url(r'^companies/(?P<slug>[-\w]+)/jobs$', JobView.as_view({'post': 'post', 'get': 'get_all_job'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)$',
        JobView.as_view({'patch': 'patch', 'delete': 'delete', 'get': 'get'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/info$', JobView.as_view({'get': 'get_job_for_other'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/applied$', JobView.as_view({'get': 'get_applied'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/shortlisted$',
        JobView.as_view({'get': 'get_shortlisted'})),

    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/apply$', JobView.as_view({'post': 'apply_for_job'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/shortlisted/(?P<user_slug>[-\w]+)$',
        JobView.as_view({'post': 'shortlist'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/un-shortlisted/(?P<user_slug>[-\w]+)$',
        JobView.as_view({'post': 'unshortlist'})),
    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/interview/(?P<user_slug>[-\w]+)',
        JobView.as_view({'post': 'interview', 'get': 'get_interview'})),

    url(r'^companies/(?P<slug>[-\w]+)/jobs/(?P<job_slug>[-\w]+)/interview$',
        JobView.as_view({'get': 'get_interview'})),

    url(r'^jobs/random$', RandomJobs.as_view()),

    url(r'^search/jobs/applied$', JobView.as_view({'get': 'get_my_applied'})),
    url(r'^search/jobs/created$', JobView.as_view({'get': 'get_my_created_job'})),

]
