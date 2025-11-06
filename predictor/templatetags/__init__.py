import json
from django import template

register = template.Library()

@register.filter(name='parse_json')
def parse_json(value):
    """Parse JSON string into Python object"""
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []
