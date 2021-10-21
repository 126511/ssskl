from django.urls import reverse
from django.shortcuts import redirect
from django import forms
from django.conf import settings
from django.forms import ModelForm
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from datetime import datetime, timedelta
from myproject.models import *
from django.core import serializers
import dateutil.parser
from django.utils import timezone

def requires_login(view):
    def new_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/login/') 
        return view(request, *args, **kwargs)
    return new_view 

def requires_profile(view):
    def new_view(request, *args, **kwargs): 
        profile = Profile.objects.filter(user=request.user).count()
        if profile < 1 or not Profile.objects.get(user=request.user).completed: 
            messages.add_message(request, messages.INFO, 'Maak eerst een profiel aan:') 
            return HttpResponseRedirect('/profile/')
        return view(request, *args, **kwargs)
    return new_view    

from django.middleware.csrf import get_token
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth import login

def get_form(model_class,excludes):
    class DynamoForm(forms.ModelForm):
        class Meta:
            model = model_class
            exclude = excludes


    return DynamoForm

def form_config(model):
    if model == 'Product':
        excludes = []
        title = 'Producten'
    elif model == 'Prepaid':
        excludes = ['processed']
        title = 'Opwaarderingen'        
    elif model == 'Stock':
        excludes = []
        title = 'Voorraad'                           
    else:
        excludes = []
        title = 'Object'

    return excludes,title

def create(request,model):

    from django.apps import apps

    excludes,title = form_config(model)

    local_model = apps.get_model('myproject', str(model))

    if request.POST:
        form = get_form(local_model,excludes=excludes)(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save()
            obj.save()
            messages.add_message(request, messages.SUCCESS, 'Object succesvol toegevoegd.') 
            form = get_form(local_model,excludes=excludes)(request.POST)
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')            
    else:
        form = get_form(local_model,excludes=excludes)

    objects = local_model.objects.all()

    return render(request, 'create_form.html', {'objects':objects, 'form':form, 'title':title, 'model':model})

def edit(request,model,id):

    from django.apps import apps

    excludes,title = form_config(model)

    local_model = apps.get_model('myproject', str(model))
    instance = local_model.objects.get(id=id)

    if request.POST:
        form = get_form(local_model,excludes=excludes)
        form = form(request.POST,request.FILES,instance=instance)
        if form.is_valid():
            obj = form.save()
            obj.save()
            messages.add_message(request, messages.SUCCESS, 'Object successvol upgedate.') 
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')            
    else:
        form = get_form(local_model,excludes=excludes)
        form = form(instance=instance)

    return render(request, 'edit_form.html', {'instance':instance, 'form':form, 'title':title, 'model':model})

def delete(request,model,id):

    from django.apps import apps

    if model == 'User':
        User.objects.get(id=id).delete()
        messages.add_message(request, messages.INFO, 'Gebruiker verwijderd.') 
        return HttpResponseRedirect('/users/') 
    if model == 'Sale':
        Sale.objects.get(id=id).delete()
        messages.add_message(request, messages.INFO, 'Aankoop ongedaan gemaakt.') 
        return HttpResponseRedirect('/')         
    else:
        local_model = apps.get_model('myproject', str(model))
        instance = local_model.objects.get(id=id)
        instance.delete()
        messages.add_message(request, messages.INFO, 'Object verwijderd.') 

        return HttpResponseRedirect('/create/'+str(model)+'/') 


def start(request):
    products = Product.objects.all()
    users = Profile.objects.exclude(user__id=1).order_by('-last_update')
    last_sale = None
    user_badges = []

    if request.POST:
        sales = 0
        buyers = []
        for buyer in users:
            #if request.POST.has_key('buyer-'+str(buyer.user.id)):
            if 'buyer-'+str(buyer.user.id) in request.POST:
                sales += 1
                sale = Sale()
                sale.cashier = request.user
                sale.buyer = buyer.user
                sale.product = Product.objects.get(id=int(request.POST['product']))
                sale.amount = int(request.POST['amount'])
                sale.save()
                buyers.append(buyer.user.id)
        if sales == 0:
            messages.add_message(request, messages.WARNING, 'Kies tenminste 1 persoon') 
        else:
            messages.add_message(request, messages.SUCCESS, 'Afgerekend :)')
            
            for buyer in buyers:
                user_badges = list(User_badge.objects.filter(user__id=buyer).values_list('badge__id',flat=True))
                for badge in Badge.objects.filter(product=Product.objects.get(id=int(request.POST['product']))).exclude(id__in=user_badges):
                    if badge.slug == 'n00b':
                        # n00b time
                        db_user = User.objects.get(id=buyer)
                        if Sale.objects.filter(product=badge.product,buyer=db_user).count()>=5:
                            user_badge = User_badge()
                            user_badge.badge = badge
                            user_badge.user = db_user
                            user_badge.save()
                            user_badges.append(user_badge.id)
                    if badge.slug == 'expert':
                        # expert time
                        db_user = User.objects.get(id=buyer)
                        if Sale.objects.filter(product=badge.product,buyer=db_user).count()>=100:
                            user_badge = User_badge()
                            user_badge.badge = badge
                            user_badge.user = db_user
                            user_badge.save()
                            user_badges.append(user_badge.id)                            
            user_badges = User_badge.objects.filter(id__in=user_badges)

    return render(request, 'start.html', {'products':products, 'users':users, 'last_sale':last_sale, 'user_badges':user_badges})

def history(request):
    users = Profile.objects.exclude(user__id=1).order_by('-last_update')
    if request.user.id == 1:
        sales = Sale.objects.all().order_by('-added_at')[:100]
    else:
        sales = Sale.objects.filter(buyer=request.user).order_by('-added_at')[:100]
    return render(request, 'history.html', {'sales':sales, 'users':users})

def graph(request):
    users = Profile.objects.exclude(user__id=1).order_by('-last_update')
    if request.user.id == 1:
        sales = Sale.objects.all().order_by('-added_at')
    else:
        sales = Sale.objects.filter(buyer=request.user).order_by('-added_at')
    return render(request, 'graph.html', {'sales':sales, 'users':users})

def balance(request):
    prepaids = Prepaid.objects.filter(buyer=request.user)
    return render(request, 'balance.html', {'prepaids':prepaids})

def inventory(request):
    stocks = Stock.objects.all()
    return render(request, 'inventory.html', {'stocks':stocks})

def users(request):
    users = Profile.objects.exclude(user__id=1).order_by('balance','-last_update')
    return render(request, 'users.html', {'users':users})


def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    #from datetimewidget.widgets import DateWidget
    from django.contrib.admin.widgets import AdminDateWidget

    class ProfileForm(ModelForm):
        class Meta:
            model = Profile
            exclude = ['user','slug','status','completed','organization','intro_completed','group','feedback_user','score','balance','image','birth']
            #widgets = {'birth':DateWidget(usel10n=True, bootstrap_version=3)}
            widgets = {'birth':AdminDateWidget} 

    if request.POST:
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            obj = form.save()
            obj.save()
            if not obj.completed:
                obj.completed = True
                messages.add_message(request, messages.SUCCESS, 'Welkom bij SSSKL :)') 
                obj.save()
                return HttpResponseRedirect('/') 

            messages.add_message(request, messages.SUCCESS, 'Profiel instellingen zijn successvol opgeslagen.') 
            profile = Profile.objects.get(user=request.user)
            form = ProfileForm(instance=profile) 
        else:
            messages.add_message(request, messages.INFO, 'Er is iets fout gegaan.')            
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'profile':profile, 'form':form})