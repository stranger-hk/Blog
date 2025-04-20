from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('generate/', views.generate_blog, name='generate_blog'),
]
