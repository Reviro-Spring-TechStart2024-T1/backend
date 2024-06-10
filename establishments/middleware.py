from django.utils.deprecation import MiddlewareMixin

from .models import Establishment


class EstablishmentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        establishment_id = request.session.get('selected_establishment')
        if establishment_id:
            try:
                request.selected_establishment = Establishment.objects.get(id=establishment_id)
            except Establishment.DoesNotExist:
                request.selected_establishment = None
        else:
            request.selected_establishment = None
