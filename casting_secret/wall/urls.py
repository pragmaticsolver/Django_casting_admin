from django.conf.urls import url

from casting_secret.wall import api

wall_url_patterns = [
    url(r'^activity/$', api.Activities.as_view(), name='activity_api'),
    url(r'^activity/saved$', api.Activities.as_view(), name='activity_saved_api'),
    url(r'^activity/(?P<pk>[0-9]+)/media$', api.Activities.as_view(), name='activity_media'),
    url(r'^activity/(?P<pk>[0-9]+)$', api.ViewActivity.as_view(), name='activity_view_post'),
    url(r'^activity/(?P<pk>[0-9]+)/like$', api.LikeActivity.as_view(), name='activity_like_post'),
    url(r'^activity/(?P<pk>[0-9]+)/unlike$', api.UnlikeActivity.as_view(), name='activity_unlike_post'),
    url(r'^activity/(?P<pk>[0-9]+)/share$', api.ShareActivity.as_view(), name='activity_share_post'),
    url(r'^activity/(?P<pk>[0-9]+)/comments$', api.Comment.as_view(), name='comment_post'),
    url(r'^activity/(?P<pk>[0-9]+)/comments/(?P<comment_id>[0-9]+)$', api.Comment.as_view(), name='comment_delete'),
    url(r'^activity/(?P<pk>[0-9]+)/bookmark$', api.ActivityBookMark.as_view(), name='bookmark_post'),
    url(r'^activity/(?P<pk>[0-9]+)/report$', api.ActivityReportAPI.as_view(), name='activity_report'),
    url(r'^activity/(?P<pk>[0-9]+)/hide', api.ActivityHideAPI.as_view(), name='activity_hide'),
    url(r'^activity/(?P<pk>[0-9]+)/remove-bookmark$', api.ActivityRemoveBookmark.as_view(),
        name='remove_bookmark_post'),

]
