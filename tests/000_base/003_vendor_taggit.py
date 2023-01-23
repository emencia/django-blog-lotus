from lotus.factories import TagsFactory


def test_factory_tags():
    """
    A very basic test to ensure the dummy factories just work since it is just some
    glue over Faker.
    """
    builder = TagsFactory()

    assert len(builder.build(5)) == 5
    assert len(builder.build(42)) == 42
