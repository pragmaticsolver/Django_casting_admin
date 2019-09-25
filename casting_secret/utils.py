from friendship.models import Friend


def mutual_friends(logged_in_user, target_user):
    logged_in_user_friends = Friend.objects.friends(logged_in_user, target_user)
    target_user_friends = Friend.objects.friends(target_user, logged_in_user)
    return logged_in_user_friends.intersection(target_user_friends)
