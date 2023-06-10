from lotus.factories import ArticleFactory
from lotus.templatetags.lotus import check_object_lang_availability


def test_check_object_lang_availability_basic(db, settings):
    """
    Tag should return infos about available languages and if given object set language
    attribute to an available language.
    """
    settings.LANGUAGE_CODE = "en"

    article_object = ArticleFactory(title="dummy", language="en")

    assert check_object_lang_availability({}, article_object) == {
        "is_available": True,
        "languages": (("en", "English"), ("fr", "Français"), ("de", "Deutsche")),
        "language_keys": ["en", "fr", "de"],
        "language_labels": ["English", "Français", "Deutsche"]
    }

    article_object.language = "zh"
    assert check_object_lang_availability({}, article_object)["is_available"] is False

    article_object.language = ""
    assert check_object_lang_availability({}, article_object)["is_available"] is False

    article_object.language = None
    assert check_object_lang_availability({}, article_object)["is_available"] is False

    class Dummy:
        pass

    assert check_object_lang_availability({}, Dummy())["is_available"] is False
