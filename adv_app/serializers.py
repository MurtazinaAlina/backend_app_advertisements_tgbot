from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from .models import Advertisement, Favourites


class UserSerializer(serializers.ModelSerializer):
    """Serializer для отображения пользователя"""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
        )


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    # noinspection PyUnresolvedReferences
    class Meta:
        model = Advertisement
        fields = (
            "id",
            "title",
            "description",
            "creator",
            "status",
            "created_at",
        )

        # защита полного дублирования объявления (с одним заголовком и текстом)
        # альтернатива реализации на уровне модели (там тоже реализовано)
        validators = [
            UniqueTogetherValidator(
                queryset=Advertisement.objects.all(),
                fields=["title", "description"],
                message="Объявление с таким заголовком и текстом уже существует!",
            ),
            UniqueTogetherValidator(
                queryset=Advertisement.objects.all(),
                fields=["title"],
                message="Объявление с таким заголовком уже существует!",
            ),
        ]

    def create(self, validated_data):
        """
        Метод для создания.
        Переопределяем, т.к. добавляем пользователя из контекста в методе + валидируем
        Простановка значения поля создатель по-умолчанию.
        Текущий пользователь является создателем объявления, изменить или переопределить его через API нельзя.
        """

        # Проверка количества открытых объявлений перед созданием
        open_advs_quantity = self.context["request"].user.advertisement_set.filter(status="OPEN")
        if len(open_advs_quantity) >= 10:
            raise ValidationError("У пользователя не может быть больше 10 открытых объявлений!")

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # Проверка количества открытых объявлений + запроса замены статуса перед изменением:
        # проверка обхода ограничения на количество объявлений
        open_advs_quantity = self.context["request"].user.advertisement_set.filter(status="OPEN")

        if "status" in data and data["status"] == "OPEN" and len(open_advs_quantity) >= 10:
            raise ValidationError("У пользователя не может быть больше 10 открытых объявлений!")

        return data


class AdvertisementInFavouriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения объявления в Избранном"""

    creator = serializers.ReadOnlyField(source="creator.username")

    class Meta:
        model = Advertisement
        fields = ["id", "title", "description", "creator", "created_at"]


class FavouritesSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения Избранного"""

    class Meta:
        model = Favourites
        fields = ["id", "advertisement", "added_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user

        # Проверка на добавление владельцем
        if self.context["request"].user == validated_data["advertisement"].creator:
            raise ValidationError("Нельзя добавить в избранное собственное объявление!")

        # Проверка на дублирование объявления в избранное
        id_to_add = validated_data["advertisement"].id
        advs_with_this_id_in_base = self.context["request"].user.favourites_set.filter(
            advertisement__id=id_to_add
        )
        if len(advs_with_this_id_in_base) > 0:
            raise ValidationError("Это объявление уже в избранных у пользователя!")

        # Проверка на допустимый статус объявления
        if validated_data["advertisement"].status == "DRAFT":
            raise ValidationError("Нельзя добавить в Избранное черновик!")

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["advertisement"] = AdvertisementInFavouriteSerializer(
            instance.advertisement
        ).data

        return representation
