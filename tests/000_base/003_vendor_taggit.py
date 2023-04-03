from lotus.factories import TagNameBuilder


def test_factory_tags():
    """
    A very basic test to ensure TagNameBuilder just works. Since it is just some glue
    over Faker there is not so much to check against.
    """
    builder = TagNameBuilder()

    assert len(builder.build(5)) == 5
    assert len(builder.build(42)) == 42
