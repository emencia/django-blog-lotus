import random

import faker

from django.conf import settings


def fake_html_paragraphs(
    is_html=True,
    max_nb_chars=None,
    nb_paragraphs=None,
):
    """
    Build a string of HTML paragraphs with ``Faker.text``.

    Default values for paragraph length and sentence character length have been
    defined to never be over 500 characters for the whole content.

    NOTE: There is a bug with factoryboy 3.1.0 to 3.2.0 and ``Factory.generate()``
    usage which does not use given Factory parameters and instead require them
    in the parameters in ``generate``. Once a bug fix release is released, we
    may turn to use again factory.Faker().

    Keyword Arguments:
        is_html (boolean): If True, every paragraph will be surrounded with an
            HTML paragraph markup. Default is True.
        max_nb_chars (integer): Number of characters limit to create each
            paragraph. Default is None so a random number between 50 and 100
            will be used at each paragraph.
        nb_paragraphs (integer): Number of paragraphs to create in content.
            Default is None so a random number between 2 and 4 will be used.

    Returns:
        string: HTML content for paragraphs.
    """
    container = "<p>{:s}</p>" if is_html else "{:s}"
    nb_paragraphs = nb_paragraphs or random.randint(2, 4)
    max_nb_chars = max_nb_chars or random.randint(50, 100)
    paragraphs = []

    for _ in range(nb_paragraphs):
        text = faker.Faker(
            locale=settings.LANGUAGE_CODE
        ).text(
            max_nb_chars=max_nb_chars,
        ).replace("\n", "")

        paragraphs.append(text)

    body = [container.format(p) for p in paragraphs]

    return "".join(body)
