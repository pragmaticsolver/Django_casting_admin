from casting_secret.exception import UnsupportedMimeTypeException


def check_file_type(file):
    kind = str(file.content_type)
    if 'image' in kind:
        return 'IMG'
    elif 'video' in kind:
        return 'VIDEO'
    elif 'audio' in kind:
        return 'AUDIO'
    else:
        raise UnsupportedMimeTypeException


def is_image(file):
    kind = str(file.content_type)
    if 'image' in kind:
        return True
        raise UnsupportedMimeTypeException
