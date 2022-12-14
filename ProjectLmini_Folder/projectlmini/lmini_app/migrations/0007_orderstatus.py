# Generated by Django 4.1 on 2022-09-12 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lmini_app", "0006_alter_inventory_profit_alter_inventory_totalcost_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="orderstatus",
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
                ("orderno", models.CharField(max_length=30)),
                ("status", models.CharField(max_length=30)),
                ("nooflines", models.IntegerField(default=0)),
                ("linesreceived", models.IntegerField(default=0)),
                ("totalqty", models.IntegerField(default=0)),
                ("qtyreceived", models.IntegerField(default=0)),
                ("createdate", models.DateTimeField(auto_now_add=True)),
                ("closeddate", models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
