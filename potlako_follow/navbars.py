from django.conf import settings

from edc_navbar import NavbarItem, site_navbars, Navbar

potlako_follow = Navbar(name='potlako_follow')
no_url_namespace = True if settings.APP_NAME == 'potlako_follow' else False

potlako_follow.append_item(
    NavbarItem(name='potlako_follow',
               label='Potlako follow',
               fa_icon='fa-cogs',
               url_name='potlako_follow:home_url'))

potlako_follow.append_item(
    NavbarItem(
        name='appointment_worklist',
        title='Appointments Worklist',
        label='Appointments Worklist',
        fa_icon='fa-user-plus',
        url_name=settings.DASHBOARD_URL_NAMES[
            'potlako_follow_listboard_url'],
        no_url_namespace=no_url_namespace))

potlako_follow.append_item(
    NavbarItem(
        name='investigation_fu_worklist',
        title='Investigation Worklist',
        label='Investigation Worklist',
        fa_icon='fa-user-plus',
        url_name=settings.DASHBOARD_URL_NAMES[
            'potlako_investigation_listboard_url'],
        no_url_namespace=no_url_namespace))

potlako_follow.append_item(
    NavbarItem(
        name='navigation_worklist',
        title='Navigation Plan Worklist',
        label='Navigation Plan Worklist',
        fa_icon='fa-user-plus',
        url_name=settings.DASHBOARD_URL_NAMES[
            'potlako_navigation_listboard_url'],
        no_url_namespace=no_url_namespace))

potlako_follow.append_item(
    NavbarItem(
        name='potlako_follow_admin',
        title='Potlako Follow Admin',
        label='Potlako Follow Admin',
        fa_icon='fa-cogs',
        url_name='potlako_follow:admin_url',
        no_url_namespace=no_url_namespace))


site_navbars.register(potlako_follow)
