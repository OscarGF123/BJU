from django.db import connection
from django.http import JsonResponse

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({
            "status": "healthy",
        }, status=200)

    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
        }, status=500)

def retornar_url_ngrok(request):
    import config.settings as config
    try:
        return JsonResponse({
            "status": "success",
            "url": config.CSRF_TRUSTED_ORIGINS[-1]
        })
    except Exception as e:
        return JsonResponse({"status": "error", 
                             "message": "ocurrio un error inesperado al intentar retornar la url de ngrok"
                             }, status=500)