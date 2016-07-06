from django import template
# Functions in this file are used to create custom template tags
# See also https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def dictionary(Dict, key):
    return Dict[key]