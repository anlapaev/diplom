from django import template

register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None


@register.filter
def rupluralize(value, arg=""):
    """Return the correct Russian plural form for the given number.

    ``arg`` must contain three comma-separated forms (for 1, 2-4 and 5+).
    Example: ``{{ num|rupluralize:"\u043a\u0443\u0440\u0441,\u043a\u0443\u0440\u0441\u0430,\u043a\u0443\u0440\u0441\u043e\u0432" }}``
    """
    forms = [f.strip() for f in arg.split(',')]
    if len(forms) != 3:
        return ''
    try:
        n = abs(int(value))
    except (TypeError, ValueError):
        return ''

    if n % 10 == 1 and n % 100 != 11:
        form = forms[0]
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        form = forms[1]
    else:
        form = forms[2]
    return form
