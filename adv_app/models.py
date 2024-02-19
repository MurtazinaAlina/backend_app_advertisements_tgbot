from django.db import models
from django.contrib.auth.models import User
from django.core import validators


class AdvertisementStatusChoices(models.TextChoices):
    """Статусы объявлений"""

    OPEN = "OPEN", "Открыто"
    CLOSED = "CLOSED", "Закрыто"
    DRAFT = "DRAFT", "Черновик"


# noinspection PyUnresolvedReferences
class Advertisement(models.Model):
    """Объявления"""

    title = models.TextField(
        verbose_name="Заголовок",
        validators=[
            validators.MinLengthValidator(
                5, message="Заголовок должен содержать не менее 5 символов"
            )
        ],
    )
    description = models.TextField(
        verbose_name="Описание",
        validators=[
            validators.MinLengthValidator(
                5, message="Описание должно содержать не менее 5 символов"
            )
        ],
    )
    status = models.TextField(
        verbose_name="Статус",
        choices=AdvertisementStatusChoices.choices,
        default=AdvertisementStatusChoices.OPEN,
        error_messages="Некорректное значение статуса",
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создатель",
    )
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения", auto_now=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        unique_together = ("creator", "title", "description")
        ordering = ("-id",)

    def __str__(self):
        return f"id:{self.id} {self.title}"


# noinspection PyUnresolvedReferences
class Favourites(models.Model):
    """Избранные объявления"""

    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, verbose_name="Объявление"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favourites", verbose_name="Пользователь"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        unique_together = ("advertisement", "user")

    def save(self, *args, **kwargs):
        """
        Добавить в избранное можно только объявления других пользователей и только в статусе 'OPEN'
        """
        if self.user != self.advertisement.creator:
            if self.advertisement.status == "OPEN":
                return super(Favourites, self).save(*args, **kwargs)

    def __str__(self):
        return f"id:{self.id} {self.user} - {self.advertisement.title} от {self.advertisement.creator.username}"
