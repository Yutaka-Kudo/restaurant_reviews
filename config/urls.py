"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from scrape.urls import router as scrape_router
# from scrape.urls import router_custom as scrape_router_custom

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scrape/', include('scrape.urls')),
    # path('', include('display.urls')),
    path('api/', include(scrape_router.urls)),
    # path('api/search/', include(scrape_router_custom.urls)),

    # re_path('', TemplateView.as_view(template_name='index.html')),
]
