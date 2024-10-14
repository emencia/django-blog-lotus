DISKETTE_DEFINITIONS = [
    [
        "lotus",
        {
            "comments": "Lotus weblog",
            "natural_foreign": True,
            "models": [
                "lotus.Album",
                "lotus.AlbumItem",
                "lotus.Article_categories",
                "lotus.Article_related",
                "lotus.Article",
                "lotus.Category"
            ],
            "excludes": [
                "lotus.Author",
                "lotus.Article_authors",
            ]
        }
    ]
]
"""
`Diskette <https://diskette.readthedocs.io/>`_ configuration that you can use in your
project.
"""
