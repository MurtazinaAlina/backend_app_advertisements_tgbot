from django_filters import rest_framework as filters, DateFromToRangeFilter, CharFilter

from .models import Advertisement, Favourites


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    created_at = DateFromToRangeFilter()  # работает в логике after/before к date/datetime полю
    # ?created_at_after=2020-01-01
    # ?created_at_before=2020-01-01

    class Meta:
        model = Advertisement
        fields = ["created_at", "creator", "status"]


class FavouritesFilter(filters.FilterSet):
    """Фильтры для Избранного"""

    added_at = DateFromToRangeFilter()

    class Meta:
        model = Favourites
        fields = ["added_at", "advertisement__title"]
