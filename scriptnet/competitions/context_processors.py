from .forms import LanguageForm


def language_form_context_processor(request):
    return {
        'language_form': LanguageForm({'language': request.LANGUAGE_CODE}),
    }
