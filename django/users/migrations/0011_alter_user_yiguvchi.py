# Generated by Django 5.0 on 2025-05-10 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_yiguvchi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='yiguvchi',
            field=models.BooleanField(default=False, verbose_name='Tayyorlovchi'),
        ),
    ]
