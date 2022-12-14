# Generated by Django 4.1 on 2022-09-08 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lmini_app", "0003_stockorder_transactions_orderno"),
    ]

    operations = [
        migrations.CreateModel(
            name="Inventory",
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
                ("description", models.CharField(max_length=128)),
                ("packqty", models.IntegerField(default=0)),
                ("pendingqty", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="StockValue",
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
                ("totalcost", models.IntegerField(default=0)),
                ("totalvalue", models.IntegerField(default=0)),
                ("profit", models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name="productmaster",
            name="itemcode",
            field=models.CharField(default="hi", max_length=30),
            preserve_default=False,
        ),
    ]
