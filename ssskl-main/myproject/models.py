from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
#from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
from django.core.validators import RegexValidator
import binascii
import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

def make_filepath(field_name, instance, filename):
    '''
        Produces a unique file path for the upload_to of a FileField.

        The produced path is of the form:
        "[model name]/[field name]/[random name].[filename extension]".
    '''
    new_filename = "%s.%s" % (User.objects.make_random_password(10),
                             filename.split('.')[-1])
    return '/'.join([instance.__class__.__name__.lower(),
                     field_name, new_filename])

from functools import partial

def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='_'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='_'):
    import re
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value

STATUS = (
    (1, ("In afwachting")),
    (2, ("Goedgekeurd")),
    (3, ("Geannuleerd")),  
)
from versatileimagefield.fields import VersatileImageField

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS, default=1) 
    intro_completed = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True) 
    slug = models.SlugField(max_length=255,blank=True)
    image = VersatileImageField( 'Image', upload_to='images/profile/',null=True,blank=True)
    last_update = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=200, default='' ,verbose_name = "Voornaam")
    last_name = models.CharField(max_length=200, default='',verbose_name = "Achternaam")  
    birth = models.DateField(verbose_name = "Geboortedatum", blank=True,null=True)
    tel = models.CharField(max_length=10, validators=[RegexValidator(regex='^((06){1}[1-9]{1}[0-9]{7})$', message='Het telefoonnummer moet 10 cijfers bevatten en beginnen met "06".', code='nomatch')], blank=True,verbose_name = "Mobiel Telefoonnummer (0612345678)")
    balance = models.FloatField(default=0)    

    def get_absolute_url(self):
        return "/profiel/"+str(self.slug)+"/"

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name +' '+ self.last_name[:1]
        elif self.first_name:
            return self.first_name
        else:
            return str(self.user)        


class Brand(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255,verbose_name="Naam")
    price = models.FloatField(default=.5,verbose_name="Prijs")
    #stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        return super(Product, self).save(*args, **kwargs)  
        if Stock.objects.filter(product=self).count()==0:
            s = Stock()
            s.product = self
            s.amount = 0
            s.price = .2
            s.save()


class Prepaid(models.Model):
    buyer = models.ForeignKey(User, verbose_name = "Koper", on_delete=models.PROTECT)
    amount = models.FloatField(verbose_name = "Aantal euro's")
    added_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if self.processed == False and self.amount:
            self.processed = True
            p = Profile.objects.get(user=self.buyer)
            p.balance = p.balance + self.amount
            p.save()
        return super(Prepaid, self).save(*args, **kwargs)    

    def delete(self):
        p = Profile.objects.get(user=self.buyer)
        p.balance = p.balance - self.amount
        p.save()        
        super(Prepaid, self).delete()

class Sale(models.Model):
    cashier = models.ForeignKey(User,related_name="cashier", on_delete=models.PROTECT)
    buyer = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.FloatField(null=True,blank=True)
    amount = models.FloatField()
    sum = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True) 

    def save(self, *args, **kwargs):
        self.price = self.product.price
        p = Profile.objects.get(user=self.buyer)
        p.balance = p.balance - (self.amount * self.price)
        p.save()
        s = Stock.objects.get(product=self.product)
        s.amount = s.amount - self.amount

        return super(Sale, self).save(*args, **kwargs)

    def delete(self):
        p = Profile.objects.get(user=self.buyer)
        p.balance = p.balance + (self.amount * self.price)
        p.save()
        s = Stock.objects.get(product=self.product)
        s.amount = s.amount + self.amount
        s.save()   
        super(Sale, self).delete()

    def product_sum(self):
        from django.db.models import Sum
        return Sale.objects.filter(buyer=self.buyer,added_at__lt=self.added_at).aggregate(Sum('amount'))

class Stock(models.Model):
    product = models.ForeignKey(Product,related_name="product_stock", on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name = "Aantal")
    price = models.FloatField(verbose_name = "Inkoopprijs per stuk")
    added_at = models.DateTimeField(auto_now_add=True) 

class Badge(models.Model):
    name = models.CharField(max_length=200, default='' , verbose_name = "Titel")
    slug = models.CharField(max_length=200, default='' , verbose_name = "slug")
    message = models.TextField()
    product = models.ForeignKey(Product,verbose_name="Betreffend product", on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Afbeelding")

    def __str__(self):
        return self.name

class User_badge(models.Model):
    added_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.badge.name