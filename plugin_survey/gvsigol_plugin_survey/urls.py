from django.conf.urls import url

urlpatterns = [
    url(r'^survey/survey_list/$', 'gvsigol_plugin_survey.views.survey_list', name='survey_list'),
    url(r'^survey/survey_add/$', 'gvsigol_plugin_survey.views.survey_add', name='survey_add'),
    url(r'^survey/survey_update/(?P<survey_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_update', name='survey_update'),
    url(r'^survey/survey_delete/(?P<survey_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_delete', name='survey_delete'),
    url(r'^survey/survey_section_add/(?P<survey_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_section_add', name='survey_section_add'),
    url(r'^survey/survey_section_update/(?P<survey_section_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_section_update', name='survey_section_update'),
    url(r'^survey/survey_section_delete/(?P<survey_section_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_section_delete', name='survey_section_delete'),
    
    url(r'^survey/survey_definition/(?P<survey_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_definition', name='survey_definition'),
    url(r'^survey/survey_update_project/(?P<survey_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_update_project', name='survey_update_project'),
    
    url(r'^survey/survey_section_update_project/(?P<section_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_section_update_project', name='survey_section_update_project'),
    url(r'^survey/survey_permissions/(?P<survey_id>[0-9]+)/$', 'gvsigol_plugin_survey.views.survey_permissions', name='survey_permissions'),
    url(r'^surveys/upload/$', 'gvsigol_plugin_survey.views.survey_upload_db', name='survey_upload_db'),

    url(r'^surveys/$', 'gvsigol_plugin_survey.views.surveys', name='surveys'),
    url(r'^surveys/(?P<survey_name>[a-zA-Z0-9_]+)/$', 'gvsigol_plugin_survey.views.survey_definition_by_name', name='survey_definition_by_name'),
    url(r'^surveys/upload_db/$', 'gvsigol_plugin_survey.views.survey_upload', name='survey_upload'),
]