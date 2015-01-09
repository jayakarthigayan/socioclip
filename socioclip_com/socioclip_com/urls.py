from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    url(r'^$', 'socioclip.views.index', name='index'),
    url(r'^createcookie/$', 'socioclip.views.createcookie', name='createcookie'),
    url(r'^login/$', 'socioclip.views.login', name='login'),
    url(r'^signup/$', 'socioclip.views.signup', name='signup'),
    url(r'^home/$', 'socioclip.views.home', name='home'),
    url(r'^logout/$', 'socioclip.views.logout', name='logout'),
    url(r'^archive/$', 'socioclip.views.archive', name='archive'),
    url(r'^clipcount/$', 'socioclip.views.clipcount', name='clipcount'),
    url(r'^viewarchive/$', 'socioclip.views.viewarchive', name='viewarchive'),
    url(r'^createfolder/$', 'socioclip.views.createfolder', name='createfolder'),
    url(r'^(viewarchive)/(\d+)/$', 'socioclip.views.viewfoldercont', name='viewfoldercont'),
    url(r'^(home)/(\d+)/$', 'socioclip.views.viewfoldercont', name='viewfoldercont'),
    url(r'^movebookmark/$', 'socioclip.views.movebookmark', name='movebookmark'),
    url(r'^subfolders/$', 'socioclip.views.getsubfolderlist', name='getsubfolderlist'),
    url(r'^createbookmark/$', 'socioclip.views.createbookmark', name='createbookmark'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
]
