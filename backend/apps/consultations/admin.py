from django.contrib import admin

from .models import Consultation, ConsultationMessage


admin.site.register(Consultation)
admin.site.register(ConsultationMessage)

