from os import environ


def process_ui_views(request):
    return {'build': environ.get('BUILD_HASH', None)}