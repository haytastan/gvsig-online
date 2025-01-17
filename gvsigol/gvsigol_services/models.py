from __future__ import unicode_literals
# -*- coding: utf-8 -*-

'''
    gvSIG Online.
    Copyright (C) 2010-2017 SCOLAB.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
'''
@author: Javier Rodrigo <jrodrigo@scolab.es>
'''
from django.db import models
from gvsigol_auth.models import UserGroup
from gvsigol import settings

class Workspace(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    uri = models.CharField(max_length=500)
    wms_endpoint = models.CharField(max_length=500, null=True, blank=True)
    wfs_endpoint = models.CharField(max_length=500, null=True, blank=True)
    wcs_endpoint = models.CharField(max_length=500, null=True, blank=True)
    wmts_endpoint = models.CharField(max_length=500, null=True, blank=True)
    cache_endpoint = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    
class Datastore(models.Model):
    workspace = models.ForeignKey(Workspace)
    type = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=500, null=True, blank=True)
    connection_params = models.TextField()
    created_by = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.workspace.name + ":" + self.name
 
    
class LayerGroup(models.Model):
    name = models.CharField(max_length=150) 
    title = models.CharField(max_length=500, null=True, blank=True) 
    visible = models.BooleanField(default=False)
    cached = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name


class Layer(models.Model):
    datastore = models.ForeignKey(Datastore)
    layer_group = models.ForeignKey(LayerGroup)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    abstract = models.CharField(max_length=5000)
    type = models.CharField(max_length=150)
    visible = models.BooleanField(default=True)
    queryable = models.BooleanField(default=True)
    cached = models.BooleanField(default=True)
    single_image = models.BooleanField(default=False)
    time_enabled = models.BooleanField(default=False)
    time_enabled_field = models.CharField(max_length=150, null=True, blank=True) 
    time_enabled_endfield = models.CharField(max_length=150, null=True, blank=True) 
    time_presentation = models.CharField(max_length=150, null=True, blank=True) 
    time_resolution_year = models.IntegerField(null=True, default=0)
    time_resolution_month = models.IntegerField(null=True, default=0)
    time_resolution_week = models.IntegerField(null=True, default=0)
    time_resolution_day = models.IntegerField(null=True, default=0)
    time_resolution_hour = models.IntegerField(null=True, default=0)
    time_resolution_minute = models.IntegerField(null=True, default=0)
    time_resolution_second = models.IntegerField(null=True, default=0)
    time_default_value_mode = models.CharField(max_length=150, null=True, blank=True) 
    time_default_value = models.CharField(max_length=150, null=True, blank=True)
    time_resolution = models.CharField(max_length=150, null=True, blank=True)
    highlight = models.BooleanField(default=False)
    highlight_scale = models.FloatField(null=True, blank=True)
    order = models.IntegerField(default=100)
    created_by = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='thumbnails', default=settings.STATIC_URL + 'img/no_thumbnail.jpg', null=True, blank=True)
    conf = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    def get_qualified_name(self):
        return self.datastore.workspace.name + ":" + self.name

class LayerReadGroup(models.Model):
    layer = models.ForeignKey(Layer)
    group = models.ForeignKey(UserGroup)
    
    
class LayerWriteGroup(models.Model):
    layer = models.ForeignKey(Layer)
    group = models.ForeignKey(UserGroup)
    
    
class DataRule(models.Model):
    path = models.CharField(max_length=500)
    roles = models.CharField(max_length=500)

class LayerLock(models.Model):
    """locks created from geoportal"""
    GEOPORTAL_LOCK = 0
    """locks created from sync API"""
    SYNC_LOCK = 1
    """Valid lock types"""
    TYPE_CHOICES = (
        (GEOPORTAL_LOCK, 'Geoportal'),
        (SYNC_LOCK, 'Sync')
    )
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    type = models.IntegerField(choices=TYPE_CHOICES, default=GEOPORTAL_LOCK) 
    
    def __unicode__(self):
        return self.layer.name

class LayerResource(models.Model):
    """Stores resources (images, pdfs, etc) linked to specific features in a Layer"""

    """image files, stored in the file system"""
    EXTERNAL_IMAGE = 1
    """PDF files, stored in the file system""" 
    EXTERNAL_PDF = 2
    """.ODT or .DOC files, stored in the file system"""
    EXTERNAL_DOC = 3
    """any kind of resource file"""
    EXTERNAL_FILE = 4
    """video files"""
    EXTERNAL_VIDEO = 5
    """alfresco directory"""
    EXTERNAL_ALFRESCO_DIR = 6
    """Valid resource types"""
    TYPE_CHOICES = (
        (EXTERNAL_IMAGE, 'Image'),
        (EXTERNAL_PDF, 'PDF'),
        (EXTERNAL_DOC, 'DOC'),
        (EXTERNAL_VIDEO, 'Video'),
        (EXTERNAL_FILE, 'File'),
    )
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)
    """The primary key of the feature. This makes mandatory for
    gvSIG Online layers to have a numeric, non-complex primary key"""
    feature = models.IntegerField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    path = models.CharField(max_length=500)
    """The title of the resource (optional)"""
    title = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
class Enumeration(models.Model):
    name = models.CharField(max_length=150) 
    title = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name
    
class EnumerationItem(models.Model):
    enumeration = models.ForeignKey(Enumeration, on_delete=models.CASCADE)
    name = models.CharField(max_length=150) 
    selected = models.BooleanField(default=False)
    order = models.IntegerField(null=False, default=0)
    
    def __unicode__(self):
        return self.name
    
