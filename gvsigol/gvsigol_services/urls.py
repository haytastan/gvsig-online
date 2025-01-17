from django.conf.urls import url

urlpatterns = [
    url(r'^workspace_list/$', 'gvsigol_services.views.workspace_list', name='workspace_list'),
    url(r'^workspace_add/$', 'gvsigol_services.views.workspace_add', name='workspace_add'),
    url(r'^workspace_import/$', 'gvsigol_services.views.workspace_import', name='workspace_import'),
    url(r'^workspace_delete/(?P<wsid>\d+)/$', 'gvsigol_services.views.workspace_delete', name='workspace_delete'),
    url(r'^workspace_update/(?P<wid>[0-9]+)/$', 'gvsigol_services.views.workspace_update', name='workspace_update'),
    url(r'^datastore_list/$', 'gvsigol_services.views.datastore_list', name='datastore_list'),
    url(r'^datastore_add/$', 'gvsigol_services.views.datastore_add', name='datastore_add'),
    url(r'^datastore_update/(?P<datastore_id>[0-9]+)/$', 'gvsigol_services.views.datastore_update', name='datastore_update'),
    url(r'^datastore_delete/(?P<dsid>\d+)/$', 'gvsigol_services.views.datastore_delete', name='datastore_delete'),
    url(r'^backend_datastore_list/$', 'gvsigol_services.views.backend_datastore_list', name='backend_datastore_list'),
    url(r'^backend_resource_list_available/$', 'gvsigol_services.views.backend_resource_list_available', name='backend_resource_list_available'),
    url(r'^backend_resource_list_configurable/$', 'gvsigol_services.views.backend_resource_list_configurable', name='backend_resource_list_configurable'),
    url(r'^backend_resource_list/$', 'gvsigol_services.views.backend_resource_list', name='backend_resource_list'),
    url(r'^backend_fields_list/$', 'gvsigol_services.views.backend_fields_list', name='backend_fields_list'),
    url(r'^layer_list/$', 'gvsigol_services.views.layer_list', name='layer_list'),
    url(r'^layer_add/$', 'gvsigol_services.views.layer_add', name='layer_add'),
    url(r'^layer_add/(?P<layergroup_id>[0-9]+)/$', 'gvsigol_services.views.layer_add_with_group', name='layer_add_with_group'),
    url(r'^layer_permissions/(?P<layer_id>[0-9]+)/$', 'gvsigol_services.views.layer_permissions_update', name='layer_permissions_update'),
    url(r'^get_resources_from_workspace/$', 'gvsigol_services.views.get_resources_from_workspace', name='get_resources_from_workspace'),
    url(r'^layer_update/(?P<layer_id>[0-9]+)/$', 'gvsigol_services.views.layer_update', name='layer_update'),
    url(r'^layer_delete/(?P<layer_id>[0-9]+)/$', 'gvsigol_services.views.layer_delete', name='layer_delete'),
    url(r'^layer_config/(?P<layer_id>[0-9]+)/$', 'gvsigol_services.views.layer_config', name='layer_config'),
    url(r'^cache_clear/(?P<layer_id>[0-9]+)/$', 'gvsigol_services.views.cache_clear', name='cache_clear'),
    url(r'^layergroup_cache_clear/(?P<layergroup_id>[0-9]+)/$', 'gvsigol_services.views.layergroup_cache_clear', name='layergroup_cache_clear'),
    url(r'^layer_create/$', 'gvsigol_services.views.layer_create', name='layer_create'),
    url(r'^layer_create/(?P<layergroup_id>[0-9]+)/$', 'gvsigol_services.views.layer_create_with_group', name='layer_create_with_group'),
    url(r'^get_geom_tables/(?P<datastore_id>[0-9]+)/$', 'gvsigol_services.views.get_geom_tables', name='geom_tables'),
    url(r'^layergroup_list/$', 'gvsigol_services.views.layergroup_list', name='layergroup_list'),
    url(r'^layergroup_add/$', 'gvsigol_services.views.layergroup_add', name='layergroup_add'),
    url(r'^layergroup_add/(?P<project_id>[0-9]+)/$', 'gvsigol_services.views.layergroup_add_with_project', name='layergroup_add_with_project'),
    url(r'^layergroup_delete/(?P<lgid>[0-9]+)/$', 'gvsigol_services.views.layergroup_delete', name='layergroup_delete'),
    url(r'^layergroup_update/(?P<lgid>[0-9]+)/$', 'gvsigol_services.views.layergroup_update', name='layergroup_update'),
    url(r'^enumeration_list/$', 'gvsigol_services.views.enumeration_list', name='enumeration_list'),
    url(r'^enumeration_add/$', 'gvsigol_services.views.enumeration_add', name='enumeration_add'),
    url(r'^enumeration_delete/(?P<eid>[0-9]+)/$', 'gvsigol_services.views.enumeration_delete', name='enumeration_delete'),
    url(r'^enumeration_update/(?P<eid>[0-9]+)/$', 'gvsigol_services.views.enumeration_update', name='enumeration_update'),
    url(r'^get_enumeration/$', 'gvsigol_services.views.get_enumeration', name='get_enumeration'),
    url(r'^layer_boundingbox_from_data/$', 'gvsigol_services.views.layer_boundingbox_from_data', name='layer_boundingbox_from_data'),
    url(r'^add_layer_lock/$', 'gvsigol_services.views.add_layer_lock', name='add_layer_lock'),
    url(r'^remove_layer_lock/$', 'gvsigol_services.views.remove_layer_lock', name='remove_layer_lock'),
    url(r'^lock_list/$', 'gvsigol_services.views.lock_list', name='lock_list'),
    url(r'^unlock_layer/(?P<lock_id>[0-9]+)/$', 'gvsigol_services.views.unlock_layer', name='unlock_layer'),
    url(r'^get_feature_info/$', 'gvsigol_services.views.get_feature_info', name='get_feature_info'),
    url(r'^get_feature_resources/$', 'gvsigol_services.views.get_feature_resources', name='get_feature_resources'),
    url(r'^get_datatable_data/$', 'gvsigol_services.views.get_datatable_data', name='get_datatable_data'),
    url(r'^get_unique_values/$', 'gvsigol_services.views.get_unique_values', name='get_unique_values'),
    url(r'^upload_resources/$', 'gvsigol_services.views.upload_resources', name='upload_resources'),
    url(r'^delete_resource/$', 'gvsigol_services.views.delete_resource', name='delete_resource'),
    url(r'^delete_resources/$', 'gvsigol_services.views.delete_resources', name='delete_resources'),
    url(r'^describeFeatureType/$', 'gvsigol_services.views.describeFeatureType', name='describeFeatureType'),
    url(r'^describeFeatureTypeWithPk/$', 'gvsigol_services.views.describeFeatureTypeWithPk', name='describeFeatureTypeWithPk'),
    url(r'^base_layer/base_layer_list/$', 'gvsigol_services.views.base_layer_list', name='base_layer_list'),
    url(r'^base_layer/base_layer_add/$', 'gvsigol_services.views.base_layer_add', name='base_layer_add'),
    url(r'^base_layer/base_layer_update/(?P<base_layer_id>[0-9]+)/$', 'gvsigol_services.views.base_layer_update', name='base_layer_update'),
    url(r'^base_layer/base_layer_delete/(?P<base_layer_id>[0-9]+)/$', 'gvsigol_services.views.base_layer_delete', name='base_layer_delete'),
    url(r'^base_layer/get_capabilities_from_url/$', 'gvsigol_services.views.get_capabilities_from_url', name='base_layer_delete'),

    url(r'^layers_get_temporal_properties/$', 'gvsigol_services.views.layers_get_temporal_properties', name='layers_get_temporal_properties'),
    url(r'^get_date_fields_from_resource/$', 'gvsigol_services.views.get_date_fields_from_resource', name='get_date_fields_from_resource'),
    
    url(r'^get_geoserver_info/$', 'gvsigol_services.views.get_geoserver_info', name='get_geoserver_info'),
    
    url(r'^describeLayerConfig/$', 'gvsigol_services.views.describeLayerConfig', name='describeLayerConfig'),
    
]