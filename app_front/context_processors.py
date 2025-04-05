from django.conf import settings

def debug_context(request):
    return {'debug': settings.DEBUG,'wss_url': settings.WSS_URL}