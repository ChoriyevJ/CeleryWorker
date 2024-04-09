from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('flat/', views.FlatAPIView.as_view(),
         name='flat_list')
]


