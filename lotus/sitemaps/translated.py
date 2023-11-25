from django.contrib.sitemaps import Sitemap


class TranslatedSitemapAbstract(Sitemap):
    model = None

    def _urls(self, page, protocol, domain):
        """
        Overwrite original Sitemap method to properly manage translations.

        Opposed to the default Django implementation that prefix alternate items the
        same URL with language, this one will have real translation URL in 'alternate'
        elements that can be different. This assume that items are only original
        object, not translations.
        """
        urls = []
        latest_lastmod = None
        all_items_lastmod = True

        paginator_page = self.paginator.page(page)
        for item in paginator_page.object_list:
            loc = f"{protocol}://{domain}{self._location(item)}"
            priority = self._get("priority", item)
            lastmod = self._get("lastmod", item)

            if all_items_lastmod:
                all_items_lastmod = lastmod is not None
                if all_items_lastmod and (
                    latest_lastmod is None or lastmod > latest_lastmod
                ):
                    latest_lastmod = lastmod

            url_info = {
                "item": item,
                "location": loc,
                "lastmod": lastmod,
                "changefreq": self._get("changefreq", item),
                "priority": str(priority if priority is not None else ""),
                "alternates": [],
            }

            if self.translations:
                for translation in self.model.objects.get_siblings(source=item):
                    loc = "{protocol}://{domain}{url}".format(
                        protocol=protocol,
                        domain=domain,
                        url=translation.get_absolute_url(),
                    )
                    url_info["alternates"].append(
                        {
                            "location": loc,
                            "lang_code": translation.language,
                        }
                    )

            urls.append(url_info)

        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod

        return urls
