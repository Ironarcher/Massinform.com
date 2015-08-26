from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view2, name='notify_index'),
    url(r'^createcontact/$', views.createContact),
    url(r'^deletecontact/$', views.deleteContact),
]