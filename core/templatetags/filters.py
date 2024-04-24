from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

register = template.Library()


@register.filter
def highlight_code(value, filename):
    try:
        lexer = get_lexer_for_filename(filename)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    formatter = HtmlFormatter(style='default', linenos='inline', noclasses=True)
    return mark_safe(highlight(value, lexer, formatter))
