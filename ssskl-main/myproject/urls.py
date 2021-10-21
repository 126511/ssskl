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
from django.conf.urls import patterns, url, include
from django.contrib.auth.models import User, Group
from django.conf.urls import patterns, url, include
from django.http import HttpResponse

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'', include(frontend_urls)),
    url(r'^$', requires_login(requires_profile(myproject.views.start)), name='start'),    
    url(r'^history/', requires_login(requires_profile(myproject.views.history)), name='history'),   
    url(r'^graph/', requires_login(requires_profile(myproject.views.graph)), name='graph'),   
    url(r'^balance/', requires_login(requires_profile(myproject.views.balance)), name='balance'),   
    url(r'^inventory/', requires_login(requires_profile(myproject.views.inventory)), name='inventory'), 
    url(r'^users/', requires_login(requires_profile(myproject.views.users)), name='users'), 
    url(r'^profile/', myproject.views.profile, name='profile'),  
    url(r'^create/(?P<model>\w+)/', myproject.views.create, name='create'),
    url(r'^edit/(?P<model>\w+)/(?P<id>\d+)/', myproject.views.edit, name='edit'),
    url(r'^delete/(?P<model>\w+)/(?P<id>\d+)/', myproject.views.delete, name='delete'),
    url(r'^accounts/', include('allauth.urls')),    
]
