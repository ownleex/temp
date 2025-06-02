from django.urls import path
from . import views

urlpatterns = [
    # Tchat général
    path('general/messages/', views.GeneralMessageListView.as_view(), name='general_message_list'),
    path('general/send/', views.GeneralMessageSendView.as_view(), name='general_send_message'),

    path('private/send/<int:receiver_player_id>/', views.PrivateMessageSendView.as_view(), name='private-message-send'),
    path('private/list/', views.PrivateMessageListView.as_view(), name='private-message-list'),

    path('api/status/', views.StatusApi.as_view(), name='status'),
]
