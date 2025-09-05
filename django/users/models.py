from django.db import models

class User(models.Model):
    name = models.CharField(verbose_name='Fullname', max_length=100)
    username = models.CharField(verbose_name='Username', max_length=100, null=True,blank=True)
    user_id = models.BigIntegerField(verbose_name='Telegram_id', unique=True, default=1)
    phone_number = models.BigIntegerField(verbose_name='Telefon raqami',blank=True,null=True)
    saler_id = models.BigIntegerField(verbose_name='Saler ID',blank=True,null=True)
    client_id = models.BigIntegerField(verbose_name='Client ID',blank=True,null=True)
    is_blocked = models.BooleanField(default=False,verbose_name="Bloklash")
    yiguvchi = models.BooleanField(default=False,verbose_name="Yiguvchi")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan sana")
    def __str__(self):
        return self.name
    