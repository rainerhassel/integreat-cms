import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from ...utils.translation_utils import mt_to_lang_is_permitted

logger = logging.getLogger(__name__)


class MachineTranslationForm(forms.Form):
    """
    Form for selecting target languages for machine translation of a content object.
    """

    automatic_translation = forms.BooleanField(
        widget=forms.CheckboxInput(),
        required=False,
        label=_("Automatic translation"),
        help_text=_(
            "Tick if updating this content should automatically refresh or create its translations."
        ),
    )

    translations_to_update = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=None,
        required=False,
        label=_("Update existing translations:"),
    )

    translations_to_create = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=None,
        required=False,
        label=_("Create new translations:"),
    )

    def __init__(self, instance, region, language, **kwargs):
        r"""
        Initialize MT translation form

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict
        """
        super().__init__(**kwargs)

        parent_node = region.language_node_by_slug.get(language.slug)
        translation_targets = [
            language_node
            for language_node in region.language_tree
            if language_node.parent_id
            and language_node.parent_id == parent_node.id
            and language_node.mt_provider
            and mt_to_lang_is_permitted(region, language_node.slug)
        ]

        # completely hide options if no target languages exist
        if not translation_targets:
            del self.fields["automatic_translation"]
            return

        to_update, to_create = [], []
        for target in translation_targets:
            target_type = (
                to_update
                if instance and instance.get_translation(target.slug)
                else to_create
            )
            target_type.append(target.id)

        self.fields[
            "translations_to_update"
        ].queryset = region.language_tree_nodes.filter(id__in=to_update)
        self.fields[
            "translations_to_create"
        ].queryset = region.language_tree_nodes.filter(id__in=to_create)

        self.initial["translations_to_update"] = to_update

    def clean(self):
        """
        Validate form fields which depend on each other, see :meth:`django.forms.Form.clean`

        :return: The cleaned form data
        :rtype: dict
        """
        cleaned_data = super().clean()

        if not cleaned_data["automatic_translation"]:
            cleaned_data["translations_to_update"] = []
            cleaned_data["translations_to_create"] = []
        return cleaned_data

    def get_target_language_slugs(self):
        """
        Return the slugs of all selected target languages

        :return: The target language slugs
        :rtype: list [ str ]
        """
        return (
            self.cleaned_data["translations_to_update"]
            .union(self.cleaned_data["translations_to_create"])
            .values_list("language__slug", flat=True)
            if self.is_valid()
            else []
        )
