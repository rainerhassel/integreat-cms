import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.list import MultipleObjectMixin

from ....xliff.utils import pages_to_xliff_file
from ...models import Page
from ...utils.pdf_utils import generate_pdf
from ...utils.translation_utils import ugettext_many_lazy as __
from ..bulk_action_views import BulkActionView

logger = logging.getLogger(__name__)


class PageBulkActionMixin(MultipleObjectMixin):
    """
    Mixin for page bulk actions
    """

    #: The model of this :class:`~integreat_cms.cms.views.bulk_action_views.BulkActionView`
    model = Page


# pylint: disable=too-many-ancestors
class GeneratePdfView(PageBulkActionMixin, BulkActionView):
    """
    Bulk action for generating a PDF document of the content
    """

    #: Whether the view requires change permissions
    require_change_permission = False
    #: Whether the public translation objects should be prefetched
    prefetch_public_translations = True

    def post(self, request, *args, **kwargs):
        r"""
        Apply the bulk action on every item in the queryset and redirect

        :param request: The current request
        :type request: ~django.http.HttpResponse

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: The redirect
        :rtype: ~django.http.HttpResponseRedirect
        """
        # Generate PDF document and redirect to it
        return generate_pdf(
            request.region,
            kwargs.get("language_slug"),
            self.get_queryset(),
        )


# pylint: disable=too-many-ancestors
class ExportXliffView(PageBulkActionMixin, BulkActionView):
    """
    Bulk action for generating XLIFF files for translations
    """

    #: Whether only public translation should be exported
    only_public = False
    #: Whether the view requires change permissions
    require_change_permission = False

    def post(self, request, *args, **kwargs):
        r"""
        Function for handling a pdf export request for pages.
        The pages get extracted from request.GET attribute and the request is forwarded to :func:`~integreat_cms.cms.utils.pdf_utils.generate_pdf`

        :param request: The current request
        :type request: ~django.http.HttpResponse

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: The redirect
        :rtype: ~django.http.HttpResponseRedirect
        """
        target_language = get_object_or_404(
            self.request.region.language_tree_nodes,
            language__slug=kwargs.get("language_slug"),
            parent__isnull=False,
        ).language

        xliff_file_url = pages_to_xliff_file(
            request, self.get_queryset(), target_language, only_public=self.only_public
        )
        if xliff_file_url:
            # Insert link with automatic download into success message
            messages.success(
                request,
                __(
                    _("XLIFF file for translation to {} successfully created.").format(
                        target_language
                    ),
                    _(
                        "If the download does not start automatically, please click {}here{}."
                    ).format(
                        f"<a data-auto-download href='{xliff_file_url}' class='font-bold underline hover:no-underline' download>",
                        "</a>",
                    ),
                ),
            )

        # Let the base view handle the redirect
        return super().post(request, *args, **kwargs)