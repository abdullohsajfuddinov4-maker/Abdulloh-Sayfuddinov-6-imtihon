from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _  # Импортируем переводчик
from users.models import CustomUser

class Category(models.Model):
    TYPES = (
        ("income", _("Доход")),   # Оборачиваем в _()
        ("outcome", _("Расход")),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь")
    )
    name = models.CharField(_("Название категории"), max_length=100)
    type = models.CharField(_("Тип"), max_length=15, choices=TYPES)

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def __str__(self):
        return self.name


class Wallet(models.Model):
    TYPE_CHOICES = (
        ("cash", _("Наличные")),
        ("uzcard", _("bank")),
        ("visa", _("Visa")),
    )

    CURRENCY_CHOICES = (
        ("UZS", _("UZS")),
        ("USD", _("USD")),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name=_("Пользователь")
    )
    name = models.CharField(_("Название кошелька"), max_length=100)
    type = models.CharField(_("Тип"), max_length=20, choices=TYPE_CHOICES)
    balance = models.DecimalField(_("Баланс"), max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(_("Валюта"), max_length=3, choices=CURRENCY_CHOICES)

    class Meta:
        verbose_name = _("Кошелек")
        verbose_name_plural = _("Кошельки")

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Transaction(models.Model):
    TYPE_CHOICES = (
        ("income", _("Доход")),
        ("outcome", _("Расход")),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь")
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("Кошелек")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Категория")
    )
    type = models.CharField(_("Тип операции"), max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(_("Сумма"), max_digits=15, decimal_places=2)
    description = models.TextField(_("Описание"), blank=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        verbose_name = _("Транзакция")
        verbose_name_plural = _("Транзакции")
    def __str__(self):
        return f'{self.wallet}{self.user}'


# -----------Transfer -------

class Transfer(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    from_wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name='outgoing_transfers')
    to_wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name='incoming_transfers')
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f'{self.user}{self.from_wallet}{self.to_wallet}'
