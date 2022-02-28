from django.urls import path, include

import itypes.views

urlpatterns = [
    path('demo', itypes.views.demo),
    path('detection', itypes.views.detection),
    path('detection_images', itypes.views.detection_images),
    path('batch_img', itypes.views.batch_img),
]