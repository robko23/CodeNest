# Create your views here.
import datetime

from django.http import HttpRequest
from django.http import HttpResponse


def current_datetime(request: HttpRequest):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
