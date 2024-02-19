from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Advertisement, Favourites
from .serializers import AdvertisementSerializer, FavouritesSerializer
from .permissions import IsOwnerOrAdminOrReadOnly, IsOwnerOrAdmin
from .filters import AdvertisementFilter, FavouritesFilter


# noinspection PyUnresolvedReferences
class AdvertisementViewSet(ModelViewSet):
    """
    ViewSet для объявлений
    """

    queryset = Advertisement.objects.exclude(status="DRAFT")
    serializer_class = AdvertisementSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AdvertisementFilter
    search_fields = ["title", "description"]

    def get_queryset(self):
        # Анонимные пользователи не могут видеть черновики
        if not self.request.user.id:
            return Advertisement.objects.exclude(status="DRAFT")

        # авторизованный пользователь не видит черновики от создателей с другим ид, отличающимся по токену
        queryset = Advertisement.objects.exclude(
            Q(status="DRAFT") & ~Q(creator__id=self.request.user.id)
        )

        return queryset

    def get_permissions(self):
        """
        Получение прав для действий.
        * Создание только зарегистрированным пользователям.
        * Изменение только владельцем объявления или админом.
        * Удаление только администратором
        """

        if self.action in ["update", "partial_update", "retrieve"]:
            return [IsOwnerOrAdminOrReadOnly()]
        elif self.action == "create":
            return [IsAuthenticated()]
        elif self.action == "destroy":
            return [IsAdminUser()]
        return []

    @action(["get"], detail=False)
    def draft_list(self, request):  # api/advertisements/draft_list/
        """Список всех черновиков авторизованного пользователя. Видит только создатель"""

        if request.user.id:
            queryset = Advertisement.objects.filter(status="DRAFT", creator=request.user)
            ser = AdvertisementSerializer(queryset, many=True)
            return Response(ser.data)
        return Response([])

    @action(["get"], detail=True)
    def draft_detail(self, request, pk=None):  # api/advertisements/4/draft_detail/
        """
        Просмотр черновика владельцем. Технически бесполезная вещь, тк черновики смотрятся
        по стандартному ретриву объявлений, если открывает создатель
        """

        obj = Advertisement.objects.get(pk=pk)

        # проверка статуса
        if obj.status != "DRAFT":
            return Response([])

        # проверка владельца объявления
        if obj.creator != request.user:
            return Response({"error": "Просмотр черновика доступен только владельцу!"})

        ser = AdvertisementSerializer(obj)
        return Response(ser.data)


# noinspection PyUnresolvedReferences
class FavouritesViewSet(ModelViewSet):
    """
    ViewSet для Избранного.
    * нельзя добавить в избранное своё объявление
    * пользователь видит только свои избранные объявления
    """

    queryset = Favourites.objects.all()
    serializer_class = FavouritesSerializer

    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = FavouritesFilter
    search_fields = ["advertisement__title", "advertisement__description"]

    def get_queryset(self):
        """
        Возвращает избранные объявления пользователя, определяя его по токену
        Только пользователь может видеть свои избранные объявления
        """

        if self.request.user.id:
            return Favourites.objects.filter(user=self.request.user)
        return None
