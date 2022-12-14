# Generated by Django 4.1 on 2022-10-04 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lmini_app", "0008_alter_stockorder_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="staging",
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
                ("stagingtype", models.CharField(max_length=30)),
                ("partnumber", models.CharField(max_length=30)),
                ("qty", models.IntegerField(default=0)),
            ],
        ),
    ]
