from django.contrib import admin

from .models import AIConversation, AIMessage, AIWebhookLog


admin.site.register(AIConversation)
admin.site.register(AIMessage)
admin.site.register(AIWebhookLog)

