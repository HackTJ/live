from django import template
import random
import string
from django.utils.crypto import get_random_string
from functools import partial
import re

register = template.Library()

register.simple_tag(get_random_string)

get_random_id = partial(get_random_string, length=6)

register.simple_tag(get_random_id, name="get_random_id")


@register.simple_tag(takes_context=True)
def with_random_id(context):
    random_id = context["random_id"]
    return get_random_id()


class RandomIdNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = get_random_id()
        return ""


@register.tag(name="random_id")
def do_random_id(parser, token):
    # https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/#setting-a-variable-in-the-context
    # This uses a regular expression to parse tag contents.

    # Splitting by None == splitting by spaces.
    tag_name, args = token.contents.split(None, 1)
    if args:
        m = re.search(r".*\s?as\s(\w+)", args)
        var_name = m.groups()[0] if m else "random_id"
    else:
        var_name = "random_id"
    return RandomIdNode(var_name)
