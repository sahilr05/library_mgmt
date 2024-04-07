from django.urls import path

import main_app.views as api_views

app_name = "main_app"
urlpatterns = [
    path("checkout", api_views.CheckoutAPI.as_view()),
    path("return", api_views.ReturnBookAPI.as_view()),
    path("reserve-book", api_views.ReserveBookAPI.as_view()),
    path("fulfill-book", api_views.FulfillBookAPI.as_view()),
]
