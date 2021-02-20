import json

from functools import wraps

from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from cms.models import Region, Language
from cms.constants import feedback_ratings


def feedback_handler(func):
    """
    Decorator definition for feedback API functions and methods

    :param func: decorated function
    :type func: ~collections.abc.Callable

    :return: return handle_feedback function
    :rtype: ~collections.abc.Callable
    """

    @csrf_exempt
    def handle_feedback(request, region_slug, language_code):
        """
        Parse feedback API request parameters

        :param request: Django request
        :type request: ~django.http.HttpRequest

        :param region_slug: slug of a region
        :type region_slug: str

        :param language_code: code of a language
        :type language_code: str

        :return: return decorated function
        :rtype: ~collections.abc.Callable
        """
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request."}, status=405)
        try:
            region = Region.objects.get(slug=region_slug)
            language = Language.objects.get(code=language_code)
        except Region.DoesNotExist:
            return JsonResponse(
                {"error": f'No region found with slug "{region_slug}"'}, status=404
            )
        except Language.DoesNotExist:
            return JsonResponse(
                {"error": f'No language found with code "{language_code}"'}, status=404
            )
        if request.content_type == "application/json":
            data = json.loads(request.body.decode())
        else:
            data = request.POST.dict()
        comment = data.pop("comment", "")
        rating = data.pop("rating", None)
        category = data.pop("category", None)

        if rating not in [None, "up", "down"]:
            return JsonResponse({"error": "Invalid rating."}, status=400)
        if comment == "" and not rating:
            return JsonResponse(
                {"error": "Either comment or rating is required."}, status=400
            )
        if rating == "up":
            rating_normalized = feedback_ratings.POSITIVE
        elif rating == "down":
            rating_normalized = feedback_ratings.NEGATIVE
        else:
            rating_normalized = feedback_ratings.NOT_STATED
        is_technical = category == "Technisches Feedback"
        return func(data, region, language, comment, rating_normalized, is_technical)

    return handle_feedback


def json_response(function):
    """
    This decorator can be used to catch :class:`~django.http.Http404` exceptions and convert them to a :class:`~django.http.JsonResponse`.
    Without this decorator, the exceptions would be converted to :class:`~django.http.HttpResponse`.

    :param function: The view function which should always return JSON
    :type function: ~collections.abc.Callable

    :return: The decorated function
    :rtype: ~collections.abc.Callable
    """

    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except Http404 as e:
            return JsonResponse({"error": str(e) or "Not found."}, status=404)

    return wrap
