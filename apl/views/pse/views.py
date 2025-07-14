
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json

@method_decorator(csrf_exempt, name='dispatch')
class EpaycoView(View):

    def get(self, request):
        return render(request, "pse/pse.html")

    def post(self, request):

        webhook = json.loads(request.body)
        print(f"ALERTA DE RESULTADO DE WEBHOOK {webhook}")


