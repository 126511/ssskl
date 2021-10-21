"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
# from material.frontend import urls as frontend_urls
from django.conf.urls import url
from django.contrib import admin
import myproject.views
from django.contrib import admin
from django.conf import settings
from myproject.views import requires_login, requires_profile
from django.urls import include, path, re_path
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    # re_path(r'', include(frontend_urls)),
    re_path(r'^$', requires_login(requires_profile(myproject.views.start)), name='start'),    
    re_path(r'^history/', requires_login(requires_profile(myproject.views.history)), name='history'),   
    re_path(r'^graph/', requires_login(requires_profile(myproject.views.graph)), name='graph'),   
    re_path(r'^balance/', requires_login(requires_profile(myproject.views.balance)), name='balance'),   
    re_path(r'^inventory/', requires_login(requires_profile(myproject.views.inventory)), name='inventory'), 
    re_path(r'^users/', requires_login(requires_profile(myproject.views.users)), name='users'), 
    re_path(r'^profile/', myproject.views.profile, name='profile'),  
    re_path(r'^create/(?P<model>\w+)/', myproject.views.create, name='create'),
    re_path(r'^edit/(?P<model>\w+)/(?P<id>\d+)/', myproject.views.edit, name='edit'),
    re_path(r'^delete/(?P<model>\w+)/(?P<id>\d+)/', myproject.views.delete, name='delete'),
    re_path(r'^accounts/', include('allauth.urls')), 
] + static(settings.STATIC_URL, document_root="/static/")
