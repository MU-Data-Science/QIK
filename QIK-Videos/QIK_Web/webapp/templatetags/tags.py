from django import template
from django.conf import settings

register = template.Library()

# settings value
@register.simple_tag
def get_query(input, ranking_func, kValue, searchModel):
    image_path = input.replace(settings.TOMCAT_IP_ADDR, settings.IMAGE_PATH)
    return "video_search?query_image_path=" + image_path + "&ranking_function=" + ranking_func + "&k_value=" + str(kValue) + "&search_models=" + searchModel