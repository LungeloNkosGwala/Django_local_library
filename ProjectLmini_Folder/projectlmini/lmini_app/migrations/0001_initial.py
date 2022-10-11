# Generated by Django 4.1 on 2022-09-05 21:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductMaster",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("partnumber", models.CharField(max_length=30)),
                ("productgroup", models.CharField(max_length=30)),
                ("barcode", models.CharField(max_length=30)),
                ("costprice", models.IntegerField(default=0)),
                ("saleprice", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Transactions",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("type", models.CharField(max_length=30)),
                ("partnumber", models.CharField(max_length=30)),
                ("sourceqty", models.IntegerField(default=0)),
                ("qty", models.IntegerField(default=0)),
                ("targetqty", models.IntegerField(default=0)),
                ("sourcearea", models.CharField(max_length=30)),
                ("targetarea", models.CharField(max_length=30)),
                ("holdingunit", models.CharField(max_length=30)),
                ("transactiondate", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]