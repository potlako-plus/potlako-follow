from django.urls import path
from django.views.generic.base import RedirectView
from edc_dashboard import UrlConfig
from .admin_site import potlako_follow_admin
from .views import ListboardView, HomeView, NavigationListboardView
from .views import InvestigationFUListboardView

app_name = 'potlako_follow'

subject_identifier = '066\-[0-9\-]+'
screening_identifier = '[A-Z0-9]{8}'

urlpatterns = [
    path('admin/', potlako_follow_admin.urls),
    path('home', HomeView.as_view(), name='home_url'),
    path('', RedirectView.as_view(url='admin/'), name='admin_url'),
]

potlako_follow_listboard_url_config = UrlConfig(
    url_name='potlako_follow_listboard_url',
    view_class=ListboardView,
    label='potlako_follow_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

potlako_navigation_listboard_url_config = UrlConfig(
    url_name='potlako_navigation_listboard_url',
    view_class=NavigationListboardView,
    label='potlako_navigation_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

potlako_investigation_listboard_url_config = UrlConfig(
    url_name='potlako_investigation_listboard_url',
    view_class=InvestigationFUListboardView,
    label='potlako_investigations_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

urlpatterns += potlako_follow_listboard_url_config.listboard_urls
urlpatterns += potlako_navigation_listboard_url_config.listboard_urls
urlpatterns += potlako_investigation_listboard_url_config.listboard_urls
