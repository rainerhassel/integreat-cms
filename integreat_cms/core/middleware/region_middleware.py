import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import resolve

from ...cms.models import Region

logger = logging.getLogger(__name__)


class RegionMiddleware:
    """
    Middleware class that adds the current region to the request variable
    """

    def __init__(self, get_response):
        """
        Initialize the middleware for the current view

        :param get_response: A callable to get the response for the current request
        :type get_response: ~collections.abc.Callable
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Call the middleware for the current request.
        Sets the additional attributes on the ``request`` object:

        - ``region``: The current region, based on the region slug URL parameter
        - ``available_regions``: The regions the user has access to
        - ``quick_access_regions``: The regions that are available for quick access in the top menu

        :param request: Django request
        :type request: ~django.http.HttpRequest

        :return: The response after the region has been added to the request variable
        :rtype: ~django.http.HttpResponse
        """
        user_regions = (
            request.user.regions.all()
            if request.user.is_authenticated
            else Region.objects.none()
        )
        request.region = self.get_current_region(request)
        request.available_regions = self.get_available_regions(request, user_regions)
        request.quick_access_regions = self.get_quick_access_regions(
            request, user_regions
        )
        return self.get_response(request)

    @staticmethod
    def get_current_region(request):
        """
        This method returns the current region based on the current request.
        If the request path contains a region slug, the corresponding
        :class:`~integreat_cms.cms.models.regions.region.Region` object is queried from the database.

        :param request: Django request
        :type request: ~django.http.HttpRequest

        :raises ~django.http.Http404: When the current request has a ``region_slug`` parameter, but there is no region
                                      with that slug.

        :return: The current region of this request
        :rtype: ~integreat_cms.cms.models.regions.region.Region
        """
        # Resolve current url
        resolver_match = resolve(request.path)
        if region_slug := resolver_match.kwargs.get("region_slug"):
            return get_object_or_404(Region, slug=region_slug)
        return None

    @staticmethod
    def get_available_regions(request, user_regions):
        """
        This method returns the regions available to the user based on the current request.
        Staff members and superusers have access to all regions, whereas all other users have access to their selected regions.

        :param request: Django request
        :type request: ~django.http.HttpRequest

        :param user_regions: Prefetched regions of the user
        :type user_regions: ~django.db.models.query.QuerySet [ ~integreat_cms.cms.models.regions.region.Region ]

        :return: The regions available to the user of this request
        :rtype: ~django.db.models.query.QuerySet [ ~integreat_cms.cms.models.regions.region.Region ]
        """
        if request.user.is_superuser or request.user.is_staff:
            return Region.objects.all().order_by("-last_updated")
        return user_regions

    @staticmethod
    def get_quick_access_regions(request, user_regions):
        """
        This method returns the regions that are available for quick access in this request.
        For non-staff members, the region selection consists of the regions they have access to.
        For staff members with non-empty `regions` field, it is used as a favorite setting.
        Staff members without favorite regions just have quick access to the regions that have been last updated.
        The current region is excluded.
        The list is truncated to the first :attr:`~integreat_cms.core.settings.NUM_REGIONS_QUICK_ACCESS` elements.

        :param request: The current HTTP request
        :type request: ~django.http.HttpRequest

        :param user_regions: Prefetched regions of the user
        :type user_regions: ~django.db.models.query.QuerySet [ ~integreat_cms.cms.models.regions.region.Region ]

        :return: The regions that are available for quick access in the dropdown menu
        :rtype: list [ ~integreat_cms.cms.models.regions.region.Region ]
        """
        quick_access_regions = list(
            user_regions
            if (request.user.is_superuser or request.user.is_staff)
            and len(user_regions) > 0
            else request.available_regions
        )
        if request.region in quick_access_regions:
            quick_access_regions.remove(request.region)
        return quick_access_regions[: settings.NUM_REGIONS_QUICK_ACCESS]
