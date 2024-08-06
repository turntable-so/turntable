from django.http import JsonResponse


def healthcheck(request):
    return JsonResponse({"status": "healthy"}, status=200)
