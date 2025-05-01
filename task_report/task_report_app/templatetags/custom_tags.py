import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """Extract the file name from a file path."""
    return os.path.basename(value)
