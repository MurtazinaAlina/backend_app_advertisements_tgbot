from django.contrib import admin

from adv_app.models import Advertisement, Favourites


@admin.register(Advertisement)
class AdminAdvertisement(admin.ModelAdmin):
    """Админка объявлений"""

    list_display = ["id", "status", "title", "creator"]
    list_display_links = ["id", "status", "title"]
    list_filter = ["status"]
    search_fields = ["title", "description", "creator__username"]
    search_help_text = "Поиск в заголовке и описании объявления или по логину пользователя"
    fields = ["status", "title", "description", "creator", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Favourites)
class AdminFavourites(admin.ModelAdmin):
    """Админка Избранных объявлений"""

    list_display = ["id", "user", "advertisement", "added_at"]
    list_display_links = ["id", "user", "advertisement"]
    search_fields = ["user__username", "advertisement__title", "advertisement__description"]
    search_help_text = "Поиск в заголовке и описании объявления или по логину пользователя"
    fields = ["user", "advertisement", "added_at"]
    readonly_fields = ["added_at"]
