"""massinform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^notify/', include('notify.urls')),
    url(r'^index/', 'massinform_index.index_view'),
    url(r'^admin/', include(admin.site.urls)),

    #Usermanage urls
    url(r'^login/$', 'usermanage.views.login_view'),
    url(r'^logout/$', 'usermanage.views.logout_view'),
    url(r'^register/$', 'usermanage.views.register_view'),
    url(r'^changepassword/$', 'usermanage.views.changepassword_view'),
    url(r'^reset/$', 'usermanage.views.reset_view'),
]
