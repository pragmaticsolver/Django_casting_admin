from django.core.cache import cache
from rest_framework import exceptions


class ProfileSession:
    def __init__(self, request, profile=None):
        self.req = request
        self.profile = profile
        self.key = 'PROFILE_SESSION_KEY-' + str(request.user.pk)

    def switch_to_company(self):
        cache.set(self.key, (True, self.profile), None)

    def switch_to_user(self):
        cache.set(self.key, (False, self.profile), None)

    def __get_profile_in_session(self):
        return cache.get(self.key)

    def is_authorized_company(self):
        if self.__get_profile_in_session() is not None:
            if self.__get_profile_in_session()[0]:
                return self.__get_profile_in_session()[1]
        raise exceptions.AuthenticationFailed('Unauthorized company')

    def is_authorized_user(self):
        if not self.__get_profile_in_session()[0]:
            return self.__get_profile_in_session()[1]
        raise exceptions.AuthenticationFailed('Unauthorized user')

    def is_user(self):
        return not self.__get_profile_in_session()[0]

    def is_logged_in_company(self):
        try:
            if self.__get_profile_in_session()[0]:
                return self.__get_profile_in_session()[1]['user_profile']['auth_user'][
                           'username'] == self.req.user.username
            return False
        except:
            return False

    def get_company(self):
        return cache.get(self.key)
