from .services import get_purpose


def global_variable(request):
    return {
        "purpose": get_purpose(),
    }
