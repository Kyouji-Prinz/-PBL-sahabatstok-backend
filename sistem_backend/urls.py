from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Trik Redirect: Jika dosen membuka link onrender.com, otomatis dilempar ke UI web GitHub
    path('', RedirectView.as_view(url='https://kyouji-prinz.github.io/-PBL-sahabatstok-backend/', permanent=False)),
    
    # 2. Rute API dibiarkan lewat agar frontend bisa menembak endpoint /api/predict/ dsb.
    path('', include('api_stok.urls')),
]