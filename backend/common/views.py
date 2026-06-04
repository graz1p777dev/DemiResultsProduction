from rest_framework import viewsets


class CreatedByModelViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        if "created_by" in [field.name for field in serializer.Meta.model._meta.fields]:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
