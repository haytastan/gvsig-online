'''
    gvSIG Online.
    Copyright (C) 2007-2015 gvSIG Association.

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
@author: Cesar Martinez <cmartinez@scolab.es>
'''
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_safe,require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, RequestContext
from models import Workspace, Datastore, LayerGroup, Layer, LayerReadGroup, LayerWriteGroup
from forms_services import WorkspaceForm, DatastoreForm, LayerForm, LayerUpdateForm, DatastoreUpdateForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from backend_mapservice import gn_backend, WrongElevationPattern, WrongTimePattern, backend as mapservice_backend
from gvsigol_core.models import ProjectLayerGroup
from django.utils.translation import ugettext as _
from gvsigol_auth.utils import is_admin_user
from django.core.urlresolvers import reverse
from gvsigol_auth.models import UserGroup
import gvsigol.settings
import rest_geoserver
import logging, sys
import utils
import json
import re

_valid_layer_group_name_regex=re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")


@login_required(login_url='/gvsigonline/auth/login_user/')
@require_safe
@is_admin_user
def workspace_list(request):
    response = {
        'workspaces': Workspace.objects.values()
    }
    return render_to_response('workspace_list.html', response, context_instance=RequestContext(request))

@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
@require_http_methods(["GET", "POST", "HEAD"])
def workspace_add(request):
    if request.method == 'POST':
        form = WorkspaceForm(request.POST)
        if form.is_valid():
            # first create the ws on the backend
            if mapservice_backend.createWorkspace(request.session, form.cleaned_data['name'],
                form.cleaned_data['uri'],
                form.cleaned_data['description'],
                form.cleaned_data['wms_endpoint'],
                form.cleaned_data['wfs_endpoint'],
                form.cleaned_data['wcs_endpoint'],
                form.cleaned_data['cache_endpoint']):
                    
                # save it on DB if successfully created
                newWs = Workspace(**form.cleaned_data)
                newWs.save()
                return HttpResponseRedirect(reverse('workspace_list'))
            else:
                # FIXME: the backend should raise an exception to identify the cause (e.g. workspace exists, backend is offline)
                form.add_error(None, _("Error: workspace could not be created"))
                
    else:
        form = WorkspaceForm()
            
    return render(request, 'workspace_add.html', {'form': form, 'service_base_url': mapservice_backend.getBaseUrl()})

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def workspace_import(request):
    """
    FIXME: Not implemented yet.
    Imports on gvSIG Online an existing workspace and all its depending stores, layers, styles, etc  
    """
    if request.method == 'POST':
        #form = None #FIXME
        #if form.is_valid():
         #    #get existing ws and associated resources from Geoserver REST API 
        #    pass
        ##
        # get selected ws
        # recursively import the proposed ws
        pass
    else:
        # create empty form
        # FIXME: probably does not work
        workspaces = mapservice_backend.get_workspaces()
        workspace_names = [n for n in workspaces['name']]
        querySet = Workspace.objects.all().exclude(name__in=workspace_names)
        response = {
            'workspaces': querySet.values()
        }
        return render_to_response('workspace_import.html', response, context_instance=RequestContext(request))
    
    
@login_required(login_url='/gvsigonline/auth/login_user/')
@require_POST
@is_admin_user
def workspace_delete(request, wsid):
    try:
        ws = Workspace.objects.get(id=wsid)
        if mapservice_backend.deleteWorkspace(ws, request.session):
            datastores = Datastore.objects.filter(workspace_id=ws.id)
            for ds in datastores:
                layers = Layer.objects.filter(datastore_id=ds.id)
                for l in layers:
                    mapservice_backend.deleteLayerStyles(l, request.session)
            ws.delete()
            return HttpResponseRedirect(reverse('workspace_list'))
        else:
            return HttpResponseBadRequest()
    except:
        return HttpResponseNotFound('<h1>Workspace not found{0}</h1>'.format(ws.name)) 
    
    
@login_required(login_url='/gvsigonline/auth/login_user/')
@require_safe
@is_admin_user
def datastore_list(request):
    response = {
        'datastores': Datastore.objects.values()
    }
    return render_to_response('datastore_list.html', response, context_instance=RequestContext(request))

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def datastore_add(request):
    if request.method == 'POST':
        form = DatastoreForm(request.session, request.POST)
        if form.is_valid():
            # first create the datastore on the backend
            if mapservice_backend.createDatastore(form.cleaned_data['workspace'],
                                                  form.cleaned_data['type'],
                                                  form.cleaned_data['name'],
                                                  form.cleaned_data['description'],
                                                  form.cleaned_data['connection_params'],
                                                  session=request.session):
                # save it on DB if successfully created
                newRecord = Datastore(**form.cleaned_data)
                newRecord.save()
                return HttpResponseRedirect(reverse('datastore_list'))
            else:
                # FIXME: the backend should raise an exception to identify the cause (e.g. datastore exists, backend is offline)
                form.add_error(None, _('Error: Data store could not be created'))
            
    else:
        form = DatastoreForm(request.session)
    return render(request, 'datastore_add.html', {'form': form})

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def datastore_update(request, datastore_id):
    datastore = Datastore.objects.get(id=datastore_id)
    if datastore==None:
        return HttpResponseNotFound(_('Datastore not found'))
    if request.method == 'POST':
        form = DatastoreUpdateForm(request.POST)
        if form.is_valid():
                dstype = datastore.type
                description = form.cleaned_data.get('description')
                connection_params = form.cleaned_data.get('connection_params')
                if mapservice_backend.updateDatastore(datastore.workspace.name, datastore.name,
                                                      description, dstype, connection_params,
                                                      request.session):
                    # REST API does not allow to can't change the workspace or name of a datastore 
                    #datastore.workspace = workspace
                    #datastore.name = name
                    datastore.description = description
                    datastore.connection_params = connection_params
                    datastore.save()
                    return HttpResponseRedirect(reverse('datastore_list'))
                else:
                    form.add_error(None, _("Error updating datastore"))
    else:
        form = DatastoreUpdateForm(instance=datastore)
    return render(request, 'datastore_update.html', {'form': form, 'datastore_id': datastore_id, 'workspace_name': datastore.workspace.name})

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_POST
@is_admin_user
def datastore_delete(request, dsid):
    try:
        ds = Datastore.objects.get(id=dsid)
        if mapservice_backend.deleteDatastore(ds.workspace, ds, session=request.session):
            layers = Layer.objects.filter(datastore_id=ds.id)
            for l in layers:
                mapservice_backend.deleteLayerStyles(l, session=request.session)
            Datastore.objects.all().filter(name=ds.name).delete()
            return HttpResponseRedirect(reverse('datastore_list'))
        else:
            return HttpResponseBadRequest()
    except:
        return HttpResponseNotFound('<h1>Datastore not found{0}</h1>'.format(ds.name)) 

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_safe
@is_admin_user
def layer_list(request):
    response = {
        'layers': Layer.objects.all()
    }
    return render_to_response('layer_list.html', response, context_instance=RequestContext(request))
    

@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layer_delete(request, layer_id):
    try:
        layer = Layer.objects.get(pk=layer_id)
        if mapservice_backend.deleteResource(layer.datastore.workspace, layer.datastore, layer, session=request.session):
            mapservice_backend.deleteLayerStyles(layer, session=request.session)
            gn_backend.metadata_delete(request.session, layer)
            Layer.objects.all().filter(pk=layer_id).delete()
            mapservice_backend.setDataRules(request.session)
            mapservice_backend.createOrUpdateGeoserverLayerGroup(layer.layer_group, request.session)
            return HttpResponseRedirect(reverse('datastore_list'))
        else:
            return HttpResponseBadRequest()
    except:
        return HttpResponseNotFound('<h1>Layer not found: {0}</h1>'.format(layer_id)) 

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_safe
@is_admin_user
def backend_resource_list_available(request):
    """
    Lists the resources existing on a data store, retrieving the information
    directly from the backend (which may differ from resurces available on
    Django DB). Useful to register new resources on Django DB. 
    """
    if 'id_datastore' in request.GET:
        id_ds = request.GET['id_datastore']
        ds = Datastore.objects.get(id=id_ds)
        if ds:
            resources = mapservice_backend.getResources(ds.workspace.name, ds.name, ds.type, available=True, session=request.session)
            return HttpResponse(json.dumps(resources))
    return HttpResponseBadRequest()
    

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def layer_add(request):
    if request.method == 'POST':
        form = LayerForm(request.POST)
        abstract = request.POST.get('md-abstract')
        is_visible = False
        if 'visible' in request.POST:
            is_visible = True
        
        is_queryable = False
        if 'queryable' in request.POST:
            is_queryable = True
            
        cached = False
        if 'cached' in request.POST:
            cached = True
            
        single_image = False
        if 'single_image' in request.POST:
            single_image = True
        
        if form.is_valid():
            try:
                # first create the resource on the backend
                mapservice_backend.createResource(form.cleaned_data['datastore'].workspace,
                                      form.cleaned_data['datastore'],
                                      form.cleaned_data['name'],
                                      form.cleaned_data['title'], session=request.session)
                # save it on DB if successfully created
                newRecord = Layer(**form.cleaned_data)
                newRecord.type = form.cleaned_data['datastore'].type
                newRecord.visible = is_visible
                newRecord.queryable = is_queryable
                newRecord.cached = cached
                newRecord.single_image = single_image
                newRecord.save()
                style_name = newRecord.name + '_default'
                mapservice_backend.createDefaultStyle(newRecord, style_name, session=request.session)
                mapservice_backend.setLayerStyle(newRecord.name, style_name, session=request.session)
                
                datastore = Datastore.objects.get(id=newRecord.datastore.id)
                workspace = Workspace.objects.get(id=datastore.workspace_id)
                mapservice_backend.addGridSubset(workspace, newRecord, session=request.session)
                newRecord.metadata_uuid = ''
                try:
                    if gvsigol.settings.CATALOG_MODULE:
                        properties = mapservice_backend.get_layer_properties(request.session, workspace, newRecord)
                        muuid = gn_backend.metadata_insert(request.session, newRecord, abstract, workspace, properties)
                        newRecord.metadata_uuid = muuid
                except Exception as exc:
                    logging.exception(exc)
                    newRecord.save()
                    return HttpResponseRedirect(reverse('layer_update', kwargs={'layer_id': newRecord.id}))
                newRecord.save()
                mapservice_backend.createOrUpdateGeoserverLayerGroup(newRecord.layer_group, request.session)
                return HttpResponseRedirect(reverse('layer_permissions_update', kwargs={'layer_id': newRecord.id}))
            except Exception as e:
                try:
                    msg = e.get_message()
                except:
                    msg = _("Error: layer could not be published")
                # FIXME: the backend should raise more specific exceptions to identify the cause (e.g. layer exists, backend is offline)
                form.add_error(None, msg)
    else:
        form = LayerForm()
    return render(request, 'layer_add.html', {'form': form})


@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def layer_update(request, layer_id):
    if request.method == 'POST':
        layer = Layer.objects.get(id=int(layer_id))
        workspace = request.POST.get('workspace')
        datastore = request.POST.get('datastore')
        name = request.POST.get('name')
        title = request.POST.get('title')
        #style = request.POST.get('style')
        layer_group_id = request.POST.get('layer_group')
        is_visible = False
        if 'visible' in request.POST:
            is_visible = True
        
        is_queryable = False
        if 'queryable' in request.POST:
            is_queryable = True
            
        cached = False
        if 'cached' in request.POST:
            cached = True
            
        single_image = False
        if 'single_image' in request.POST:
            single_image = True
        if not layer.metadata_uuid:
            layer.metadata_uuid = request.POST.get('metadata_uuid')
                
        old_layer_group = LayerGroup.objects.get(id=layer.layer_group_id)
        
        if mapservice_backend.updateResource(workspace, datastore, name, title, session=request.session):
            layer.title = title
            layer.cached = cached
            layer.visible = is_visible
            layer.queryable = is_queryable 
            layer.single_image = single_image 
            layer.layer_group_id = layer_group_id
            layer.save()
            
            new_layer_group = LayerGroup.objects.get(id=layer.layer_group_id)
            
            if old_layer_group.id != new_layer_group.id:
                mapservice_backend.createOrUpdateGeoserverLayerGroup(old_layer_group, request.session)
                mapservice_backend.createOrUpdateGeoserverLayerGroup(new_layer_group, request.session)                
                
            return HttpResponseRedirect(reverse('layer_permissions_update', kwargs={'layer_id': layer_id}))
            
    else:
        layer = Layer.objects.get(id=int(layer_id))
        datastore = Datastore.objects.get(id=layer.datastore.id)
        workspace = Workspace.objects.get(id=datastore.workspace_id)
        form = LayerUpdateForm(instance=layer)
        return render(request, 'layer_update.html', {'layer': layer, 'workspace': workspace, 'form': form, 'layer_id': layer_id})

@require_POST
@is_admin_user
def layer_boundingbox_from_data(request):
    try:
        #layer = Layer.objects.get(pk=layer_id)
        ws_name = request.POST['workspace']
        layer_name = request.POST['layer']
        if ":" in layer_name:
            layer_name = layer_name.split(":")[1]
        workspace = Workspace.objects.get(name=ws_name)
        layer_query_set = Layer.objects.filter(name=layer_name, datastore__workspace=workspace)
        layer = layer_query_set[0]
        mapservice_backend.updateBoundingBoxFromData(layer, request.session)   
        mapservice_backend.clearCache(workspace.name, layer, session=request.session)
        return HttpResponse('{"response": "ok"}', content_type='application/json')
    except Exception as e:
        return HttpResponseNotFound('<h1>Layer not found: {0}</h1>'.format(layer.id))

@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def cache_clear(request, layer_id):
    if request.method == 'GET':
        layer = Layer.objects.get(id=int(layer_id)) 
        datastore = Datastore.objects.get(id=layer.datastore.id)
        workspace = Workspace.objects.get(id=datastore.workspace_id)
        mapservice_backend.clearCache(workspace.name, layer, session=request.session)
        
        return redirect('layer_list')
    
@login_required(login_url='/gvsigonline/auth/login_user/')
@require_http_methods(["GET", "POST", "HEAD"])
@is_admin_user
def layergroup_cache_clear(request, layergroup_id):
    if request.method == 'GET':
        layergroup = LayerGroup.objects.get(id=int(layergroup_id)) 
        mapservice_backend.clearLayerGroupCache(layergroup.name, session=request.session)
        
        return redirect('layergroup_list')
    

@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layer_permissions_update(request, layer_id):
    if request.method == 'POST':
        assigned_read_roups = []
        for key in request.POST:
            if 'read-usergroup-' in key:
                assigned_read_roups.append(int(key.split('-')[2]))
                
        assigned_write_groups = []
        for key in request.POST:
            if 'write-usergroup-' in key:
                assigned_write_groups.append(int(key.split('-')[2]))
        
        try:     
            layer = Layer.objects.get(id=int(layer_id))
        except Exception as e:
            return HttpResponseNotFound('<h1>Layer not found{0}</h1>'.format(layer.name))
        
        # clean existing groups and assign them again
        LayerReadGroup.objects.filter(layer=layer).delete()
        for group in assigned_read_roups:
            try:
                group = UserGroup.objects.get(id=group)
                lrg = LayerReadGroup()
                lrg.layer = layer
                lrg.group = group
                lrg.save()
            except:
                pass
        
        LayerWriteGroup.objects.filter(layer=layer).delete()
        for group in assigned_write_groups:
            try:
                group = UserGroup.objects.get(id=group)
                lrg = LayerWriteGroup()
                lrg.layer = layer
                lrg.group = group
                lrg.save()
            except:
                pass
                
        mapservice_backend.setDataRules(session=request.session)
        return redirect('layer_list')
    else:
        try:
            layer = Layer.objects.get(pk=layer_id)
            groups = utils.get_all_user_groups_checked_by_layer(layer)   
            return render_to_response('layer_permissions_add.html', {'layer_id': layer.id, 'name': layer.name, 'groups': groups}, context_instance=RequestContext(request))
        except Exception as e:
            return HttpResponseNotFound('<h1>Layer not found: {0}</h1>'.format(layer_id))
   
def get_resources_from_workspace(request):
    # FIXME
    if request.method == 'POST':
        wid = request.POST.get('workspace_id')
        layer_list = Layer.objects.all()
        
        resources = []
        for r in layer_list:
            if not resource_published(r):
                datastore = Datastore.objects.get(id=r.datastore_id)
                resource = {}
                if datastore.workspace_id == int(wid):
                    resource['id'] = r.id
                    resource['name'] = r.name
                    resources.append(resource)
                
        response = {
            'resources': resources
        }     
        return HttpResponse(json.dumps(response, indent=4), content_type='application/json')
    
def resource_published(resource):
    # FIXME
    published = False
    layers = Layer.objects.all()
    for layer in layers:
        if layer.resource.id == resource.id:
            published = True
            
    return published
    

@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layergroup_list(request):
    
    layergroups_list = LayerGroup.objects.all()
    
    layergroups = []
    for lg in layergroups_list:
        if lg.name != '__default__':
            projects = []
            project_layergroups = ProjectLayerGroup.objects.filter(layer_group_id=lg.id)
            for alg in project_layergroups:
                projects.append(alg.project.name)
            layergroup = {}
            layergroup['id'] = lg.id
            layergroup['name'] = lg.name
            layergroup['title'] = lg.title
            layergroup['cached'] = lg.cached
            layergroup['projects'] = '; '.join(projects)
            layergroups.append(layergroup)
                      
    response = {
        'layergroups': layergroups
    }     
    return render_to_response('layergroup_list.html', response, context_instance=RequestContext(request))


@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layergroup_add(request):
    if request.method == 'POST':
        name = request.POST.get('layergroup_name')
        title = request.POST.get('layergroup_title')
        
        cached = False
        if 'cached' in request.POST:
            cached = True
        
        if name != '':
            if _valid_layer_group_name_regex.search(name) == None:
                message = _("Invalid layer group name: '{value}'. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=name)
                return render_to_response('layergroup_add.html', {'message': message}, context_instance=RequestContext(request))
        
            exists = False
            layergroups = LayerGroup.objects.all()
            for lg in layergroups:
                if name == lg.name:
                    exists = True
                    
            if not exists:
                layergroup = LayerGroup(
                    name = name,
                    title = title,
                    cached = cached
                )
                layergroup.save()
            
            else:
                message = _(u'Layer group name already exists')
                return render_to_response('layergroup_add.html', {'message': message}, context_instance=RequestContext(request))
            
        else:
            message = _(u'You must enter a name for layer group')
            return render_to_response('layergroup_add.html', {'message': message}, context_instance=RequestContext(request))
            
        
        return redirect('layergroup_list')
    
    else:
        return render_to_response('layergroup_add.html', {}, context_instance=RequestContext(request))
    
    
@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layergroup_update(request, lgid):
    if request.method == 'POST':
        name = request.POST.get('layergroup_name')
        title = request.POST.get('layergroup_title')
        
        cached = False
        if 'cached' in request.POST:
            cached = True
        
        layergroup = LayerGroup.objects.get(id=int(lgid))
        mapservice_backend.deleteGeoserverLayerGroup(layergroup, request.session)
        
        sameName = False
        if layergroup.name == name:
            sameName = True
            
        exists = False
        layergroups = LayerGroup.objects.all()
        for lg in layergroups:
            if name == lg.name:
                exists = True
                
        if sameName:
            layergroup.title = title
            layergroup.cached = cached
            layergroup.save()   
            mapservice_backend.createOrUpdateGeoserverLayerGroup(layergroup, request.session)
            return redirect('layergroup_list')
             
        else:      
            if not exists:   
                if _valid_layer_group_name_regex.search(name) == None:
                    message = _("Invalid layer group name: '{value}'. Identifiers must begin with a letter or an underscore (_). Subsequent characters can be letters, underscores or numbers").format(value=name)
                    return render_to_response('layergroup_add.html', {'message': message}, context_instance=RequestContext(request))
                
                layergroup.name = name
                layergroup.title = title
                layergroup.cached = cached
                layergroup.save()
                mapservice_backend.createOrUpdateGeoserverLayerGroup(layergroup, request.session)
                return redirect('layergroup_list')
                
            else:
                message = _(u'Layer group name already exists')
                return render_to_response('layergroup_update.html', {'message': message, 'layergroup': layergroup}, context_instance=RequestContext(request))

    else:
        layergroup = LayerGroup.objects.get(id=int(lgid))
        
        return render_to_response('layergroup_update.html', {'lgid': lgid, 'layergroup': layergroup}, context_instance=RequestContext(request))
    
    
@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layergroup_delete(request, lgid):        
    if request.method == 'POST':
        layergroup = LayerGroup.objects.get(id=int(lgid))
        layers = Layer.objects.filter(layer_group_id=layergroup.id)    
        for layer in layers:  
            if mapservice_backend.deleteResource(layer.datastore.workspace, layer.datastore, layer, session=request.session):
                layer.delete()
        layergroup.delete()
        mapservice_backend.deleteGeoserverLayerGroup(layergroup, request.session)
        mapservice_backend.setDataRules(session=request.session)
            
        response = {
            'deleted': True
        }     
        return HttpResponse(json.dumps(response, indent=4), content_type='application/json')

@require_http_methods(["GET", "POST", "HEAD"])
@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layer_upload(request):
    if request.method == 'POST':
        dstype = request.POST.get('id_dstype')
        abstract = request.POST.get('md-abstract')
            
        (form_class, template, file_accepts) = mapservice_backend.getUploadForm(dstype)
        if form_class is not None:
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                try:
                    layer = mapservice_backend.uploadLayer(form.cleaned_data,
                                                           dstype,
                                                           request.FILES['file'],
                                                           session=request.session)
                    mapservice_backend.setDataRules(session=request.session)
                    style_name = layer.name + '_default'
                    mapservice_backend.createDefaultStyle(layer, style_name, session=request.session)
                    mapservice_backend.setLayerStyle(layer.name, style_name, session=request.session)
                    
                    datastore = Datastore.objects.get(id=layer.datastore.id)
                    workspace = Workspace.objects.get(id=datastore.workspace_id)
                    mapservice_backend.addGridSubset(workspace, layer, session=request.session)
                    layer.type = datastore.type
                    layer.metadata_uuid = ''
                    try:
                        if gvsigol.settings.CATALOG_MODULE:
                            properties = mapservice_backend.get_layer_properties(request.session, workspace, layer)
                            muuid = gn_backend.metadata_insert(request.session, layer, abstract, workspace, properties)
                            layer.metadata_uuid = muuid
                    except Exception as exc:
                        logging.exception(exc)
                        layer.save()
                        return HttpResponseRedirect(reverse('layer_update', kwargs={'layer_id': layer.id}))
                    layer.save()
                    mapservice_backend.createOrUpdateGeoserverLayerGroup(layer.layer_group, request.session)
                    return HttpResponseRedirect(reverse('layer_permissions_update', kwargs={'layer_id': layer.id}))
                except WrongTimePattern:
                    form.add_error(None, _("Date pattern doesn't match the uploaded file"))
                except WrongElevationPattern:
                    form.add_error(None, _("Elevation pattern doesn't match the uploaded file"))
                except rest_geoserver.RequestError as e:
                    form.add_error(None, _(e.get_message()))
                except Exception as exc:
                    # ensure the ds gets cleaned if we've failed
                    # FIXME: clean up disabled at the moment, as it has security implications
                    # We should ensure which kind of exception we have got before deleting,
                    # otherwise an attacker could use this method
                    # in order to arbitrarily delete existing data stores  
                    #mapservice_backend.deleteDatastore(ds.workspace, ds, "all", session=request.session)
                    exctype, value = sys.exc_info()[:2]
                    # use unicode with error='replace' because owslib sometimes raises exceptions using unexpected encodings
                    exc_msg = unicode(str(exctype), errors='replace')+u" - "+unicode(value)  
                    logging.exception(exc_msg)
                    form.add_error(None, _("Error uploading the layer. Review the file format."))
                    form.add_error(None, exc_msg)
            data = {
                'form': form,
                'type': dstype,
                'file_accepts': file_accepts
                #'styles': styles
            }
            return render(request, template, data)
    else:
        dstype = request.GET.get('id_dstype')
        if dstype is None:
            data = { 'types':mapservice_backend.getSupportedUploadTypes() }
            return render(request, 'layer_upload_dstype.html', data)
        else:
            (form, template, file_accepts) = mapservice_backend.getUploadForm(dstype)
            if form is not None:
                '''
                styles = []
                for s in mapservice_backend.getStyles(session=request.session):
                    if s.name != 'generic':
                        style = {}
                        style['name'] = s.name
                        if s.workspace == None:
                            style['workspace'] = "*"
                        else:
                            style['workspace'] = s.workspace
                        styles.append(style)
                '''
                data = {
                    'form': form(),
                    'type': dstype,
                    'file_accepts': file_accepts
                    #'styles': styles
                }
                return render(request, template, data)
    return HttpResponseBadRequest()

@require_http_methods(["GET", "POST", "HEAD"])
@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def layer_create(request):
    if request.method == 'POST':
        layer_type = request.POST.get('id_layer_type')
        abstract = request.POST.get('md-abstract')
        (form_class, template) = mapservice_backend.getLayerCreateForm(layer_type)
        if form_class is not None:
            form = form_class(request.POST)
            if form.is_valid():
                try:
                    l = mapservice_backend.createLayer(form.cleaned_data, layer_type, session=request.session)
                    style_name = l.name + '_default'
                    mapservice_backend.createDefaultStyle(l, style_name, session=request.session)
                    mapservice_backend.setLayerStyle(l.name, style_name, session=request.session)
                    
                    datastore = Datastore.objects.get(id=l.datastore.id)
                    workspace = Workspace.objects.get(id=datastore.workspace_id)
                    mapservice_backend.addGridSubset(workspace, l, session=request.session)
                    l.metadata_uuid = ''
                    try:
                        if gvsigol.settings.CATALOG_MODULE:
                            properties = mapservice_backend.get_layer_properties(request.session, workspace, l)
                            muuid = gn_backend.metadata_insert(request.session, l, abstract, workspace, properties)
                            l.metadata_uuid = muuid
                    except Exception as exc:
                        logging.exception(exc)
                        l.save()
                        return HttpResponseRedirect(reverse('layer_update', kwargs={'layer_id': l.id}))
                    l.save()
                    mapservice_backend.createOrUpdateGeoserverLayerGroup(l.layer_group, request.session)
                    return HttpResponseRedirect(reverse('layer_permissions_update', kwargs={'layer_id': l.id}))
                except rest_geoserver.RequestError as e:
                    form.add_error(None, _(e.get_message()))
                except Exception as exc:
                    # ensure the ds gets cleaned if we've failed
                    # FIXME: clean up disabled at the moment, as it has security implications
                    # We should ensure which kind of exception we have got before deleting,
                    # otherwise an attacker could use this method
                    # in order to arbitrarily delete existing data stores  
                    #mapservice_backend.deleteDatastore(ds.workspace, ds, "all", session=request.session)
                    print exc
                    form.add_error(None, _("Error uploading the layer. Review the file format."))
            data = {
                'form': form,
                'layer_type': layer_type
            }
            return render(request, template, data)
    else:
        layer_type = request.GET.get('id_layer_type')
        if layer_type is None:
            data = { 'types':mapservice_backend.getLayerCreateTypes() }
            return render(request, 'layer_create_type_choice.html', data)
        else:
            (form_class, template) = mapservice_backend.getLayerCreateForm(layer_type)
            if form_class is not None:
                data = {
                    'form': form_class(),
                    'layer_type': layer_type
                }
                return render(request, template, data)
    return HttpResponseBadRequest()


@require_GET
@login_required(login_url='/gvsigonline/auth/login_user/')
@is_admin_user
def get_geom_tables(request, datastore_id):
    if request.method == 'GET':
        try:
            ds = Datastore.objects.get(pk=datastore_id)
            tables = mapservice_backend.getGeomColumns(ds)
            data = { 'tables': tables}
            return render(request, 'geom_table_list.html', data)
        except:
            pass
    return HttpResponseBadRequest()
