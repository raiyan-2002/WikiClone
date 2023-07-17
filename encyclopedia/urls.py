from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>/", views.entries, name="entries"),
    path("new/", views.new, name="new"),
    path("pick/", views.pick, name="random"),
    path("edit/<str:name>", views.edit, name="edit")
]
