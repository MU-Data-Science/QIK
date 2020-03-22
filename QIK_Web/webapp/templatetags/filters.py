from django import template

register = template.Library()

@register.filter(name='times')
def times(number):
    return range(number)

@register.filter(name='split')
def split(value):
    return {
        'link': str(value).split("::")[0][2:],
        'caption': str(value).split("::")[1].split(",")[0][:-1],
        'score': str(value).split("::")[1].split(",")[1],
    }