from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.indexfolder, name='indexfolder'),
	url(r'^revisar', views.revisar, name='revisar'),
	url(r'^descargar', views.descargar, name='descargar'),
	url(r'^vote', views.vote, name='vote'),
	url(r'^folder', views.folder, name='folder'),
	url(r'^signup', views.signup, name='signup'),
	url(r'^login', views.login, name='login'),
	url(r'^logout', views.logout, name='logout'),
	url(r'^profile', views.profile, name='profile'),
	url(r'^comment', views.comment, name='comment'),
	url(r'^help', views.help, name='help'),
	url(r'^bookmark', views.bookmark, name='bookmark'),
	#url(r'^testing', views.testing, name='testing'),
	url(r'^recoverpassword', views.recover, name='recover password'),
]


