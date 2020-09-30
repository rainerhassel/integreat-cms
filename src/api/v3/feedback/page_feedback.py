import json
from urllib.parse import urlparse

from django.http import HttpResponse

from cms.models import Region, PageFeedback, PageTranslation


class FeedbackData:
    """
    This class is a generic api representation of cms feedback incl. its meta information stored in the database.
    It is used to examine feedback sent to the feedback api endpoint.

    :param page_id: The id of the page this feedback is referring to, if empty the permalink is required, defaults to ``None``
    :type page_id: int, optional

    :param permalink: The permalink of the page this feedback is referring to, is empty the page_id is required, defaults to ``''``
    :type permalink: str, optional

    :param comment: The descriptive feedback string, defaults to ``''``
    :type comment: int, optional

    :param emotion: The emotion of the feedback, can be one of ``['Pos', 'Neg', 'NA']``, defaults to ``'NA'``
    :type emotion: int, optional
    """

    def __init__(self, page_id, permalink, comment, rating, category):
        self.page_id = page_id
        self.permalink = permalink
        self.comment = comment
        self.category = category
        self.rating = rating

    @classmethod
    def from_dict(cls, feedback_dict):
        return cls(
            feedback_dict.get("id", None),
            feedback_dict.get("permalink", None),
            feedback_dict.get("comment", None),
            feedback_dict.get("rating", None),
            feedback_dict.get("category", None),
        )

    def has_id(self):
        return self.__is_either_exist(self.page_id, self.permalink)

    def has_content(self):
        return self.__is_either_exist(self.comment, self.rating)

    def get_comment(self):
        return self.comment if self.comment else ""

    def get_emotion(self):
        if self.rating == "up":
            return "POS"
        if self.rating == "down":
            return "NEG"
        return "NA"

    def get_category(self):
        if self.category == "Technisches Feedback":
            return True
        return False

    @staticmethod
    def __is_either_exist(one, two):
        return one or two


# pylint: disable=unused-argument
def feedback(request, region_slug, language_code):
    if request.method != "POST":
        return HttpResponse("Invalid request method.", status=405)

    data = json.loads(request.body)
    feedback_data = FeedbackData.from_dict(data)

    if not feedback_data.has_id():
        return HttpResponse(
            f'No page found for region "{region_slug}" with permalink "{feedback_data.permalink}".',
            content_type="text/plain",
            status=404,
        )

    if not feedback_data.has_content():
        return HttpResponse(
            "Please enter a valid rating/comment.",
            content_type="text/plain",
            status=400,
        )

    region = Region.get_current_region(request)
    page = region.pages.filter(id=feedback_data.page_id).first()
    if not page:
        slug = feedback_data.permalink.split("/")[-1]
        potential_page_translation = PageTranslation.objects.get(
            slug=slug, language__code=language_code, page__region=region
        )
        feedback_data.permalink = urlparse(feedback_data.permalink).path
        if potential_page_translation.permalink.strip(
            "/"
        ) == feedback_data.permalink.strip("/"):
            page = potential_page_translation.page
        else:
            return HttpResponse("Bad request.", content_type="text/plain", status=400)

    try:
        page_feedback = PageFeedback(
            page=page,
            emotion=feedback_data.get_emotion(),
            comment=feedback_data.get_comment(),
            is_technical=feedback_data.get_category(),
        )
        page_feedback.save()
        return HttpResponse(status=200)
    except ValueError:
        return HttpResponse("Bad request.", content_type="text/plain", status=400)
