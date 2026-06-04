from django.db import models

from common.models import CreatedByModel


class ReportExport(CreatedByModel):
    class ReportType(models.TextChoices):
        SALES = "SALES", "Sales"
        INVENTORY = "INVENTORY", "Inventory"
        ORDERS = "ORDERS", "Orders"
        BONUSES = "BONUSES", "Bonuses"

    report_type = models.CharField(max_length=32, choices=ReportType.choices)
    file = models.FileField(upload_to="reports/", blank=True)
    parameters = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.report_type} export #{self.pk}"

