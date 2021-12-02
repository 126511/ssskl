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
from myproject.views import requires_login, requires_profile, requires_admin, requires_group, requires_manager, requires_superuser
from django.urls import include, path, re_path
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    # re_path(r'', include(frontend_urls)),
    re_path(r'^$', requires_login(requires_profile(requires_group(myproject.views.start))), name='start'),    
    re_path(r'^history/', requires_login(requires_profile(requires_group(myproject.views.history))), name='history'),   
    #re_path(r'^graph/', requires_login(requires_profile(myproject.views.graph)), name='graph'),   
    re_path(r'^balance/', requires_login(requires_profile(requires_group(myproject.views.balance))), name='balance'),   
    
    re_path(r'^inventory/', requires_login(requires_profile(requires_manager(myproject.views.inventory))), name='inventory'), 
    re_path(r'^users/', requires_login(requires_profile(requires_manager(myproject.views.users))), name='users'), 
    
    re_path(r'^profile/', requires_login(myproject.views.profile), name='profile'), 
    
    re_path(r'^new_group/', requires_login(requires_profile(myproject.views.new_group))), 
    re_path(r'^join_group/(?P<id>\d+)/', requires_login(requires_profile(myproject.views.join_group)), name="join_group"),
    re_path(r'^switch_group/(?P<new_group>\d+)/', requires_login(requires_profile(requires_group(myproject.views.switch_group))), name="switch_group"),
    
    re_path(r'^create/(?P<model>\w+)/', requires_login(requires_profile(requires_manager(myproject.views.create))), name='create'),
    re_path(r'^edit/(?P<model>\w+)/(?P<id>\d+)/', requires_login(requires_profile(requires_manager(myproject.views.edit))), name='edit'),
    re_path(r'^delete/(?P<model>\w+)/(?P<id>\d+)/', requires_login(requires_profile(requires_manager(myproject.views.delete))), name='delete'),
    
    re_path(r'^accounts/', include('allauth.urls')),
    re_path(r'^admin/', admin.site.urls),

] + static(settings.STATIC_URL, document_root="/static/") + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
