from django.conf.urls import url

from casting_secret.user_profile import api

profile_url_pattern = [
    url(r'^profile/lookups$', api.Lookups.as_view(), name='lookup_api'),
    url(r'^profile/(?P<slug>[-\w]+)$', api.ProfileDetails.as_view(), name='profile-details'),
    url(r'^profile/(?P<slug>[-\w]+)/update$', api.ProfileUpdate.as_view(), name='profile-update'),
    url(r'^profile/(?P<slug>[-\w]+)/training$', api.ProfileTrainingView.as_view(), name='profile-training'),
    url(r'^profile/(?P<slug>[-\w]+)/training/(?P<pk>[0-9]+)$', api.ProfileTrainingView.as_view(),
        name='profile-training'),
    url(r'^profile/(?P<slug>[-\w]+)/social$', api.ProfileSocial.as_view(), name='profile-social'),
    url(r'^profile/(?P<slug>[-\w]+)/social/(?P<pk>[0-9]+)$', api.ProfileSocial.as_view(), name='profile-social'),

    url(r'^profile/(?P<slug>[-\w]+)/friends$', api.ProfileFriendsAPI.as_view(), name='profile-friends'),
    url(r'^profile/(?P<slug>[-\w]+)/friends/accept$', api.ProfileAcceptFriendShip.as_view(),
        name='profile-friends-accept'),
    url(r'^profile/(?P<slug>[-\w]+)/friends/reject$', api.ProfileRejectFriendShip.as_view(),
        name='profile-friends-reject'),
    url(r'^profile/(?P<slug>[-\w]+)/friends-request$', api.ProfileFriendRequestsAPI.as_view(),
        name='profile-friends-request'),
    url(r'^profile/(?P<slug>[-\w]+)/activity$', api.ProfileActivity.as_view(), name='profile-activity'),
    url(r'^profile/(?P<slug>[-\w]+)/activity/bookmark$', api.ProfileActivityBookMarked.as_view(),
        name='profile-activity-bookmarked'),

    url(r'^profile/(?P<slug>[-\w]+)/hobbies$', api.ProfileHobbiesAPI.as_view(), name='profile-hobbies'),
    url(r'^profile/(?P<slug>[-\w]+)/hobbies/(?P<pk>[0-9]+)$', api.ProfileHobbiesAPI.as_view(),
        name='profile-delete-hobbies'),
    url(r'^profile/(?P<slug>[-\w]+)/video$', api.ProfileMediaVideo.as_view(), name='profile-video'),
    url(r'^profile/(?P<slug>[-\w]+)/audio$', api.ProfileMediaAudio.as_view(), name='profile-audio'),
    url(r'^profile/(?P<slug>[-\w]+)/avatar$', api.ProfileAvatar.as_view(), name='profile-avatar'),
    url(r'^profile/(?P<slug>[-\w]+)/cover$', api.ProfileCover.as_view(), name='profile-cover'),
    url(r'^profile/(?P<slug>[-\w]+)/cover/reset$', api.ProfileCover.as_view(), name='profile-cover-reset'),
    url(r'^profile/(?P<slug>[-\w]+)/album$', api.ProfileAlbum.as_view(), name='profile-album'),
    url(r'^profile/(?P<slug>[-\w]+)/album/profile$', api.ProfilePictureAlbum.as_view(), name='profile-pic-album'),
    url(r'^profile/(?P<slug>[-\w]+)/album/image$', api.ProfileAlbumUpload.as_view(), name='profile-album'),
    url(r'^profile/(?P<slug>[-\w]+)/album/(?P<pk>[0-9]+)/image$', api.ProfileAlbumUpload.as_view(),
        name='profile-album-upload'),
    url(r'^profile/(?P<slug>[-\w]+)/album/(?P<pk>[0-9]+)$', api.ProfileAlbumUpload.as_view(), name='profile-album-get'),

    url(r'^profile/(?P<slug>[-\w]+)/switch$', api.Switchtouser.as_view(), name='switch_to_user'),
    url(r'^profile/(?P<slug>[-\w]+)/settings$', api.ProfileSettingsAPI.as_view(), name='profile_settings'),
    url(r'^profile/(?P<slug>[-\w]+)/visitor$', api.ProfileVisitor.as_view(), name='profile_visitor'),
    url(r'^profile/random$', api.RandomProfiles.as_view(), name='random-profile'),
]
