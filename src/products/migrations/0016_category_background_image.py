# Generated by Django 2.1.3 on 2019-02-04 06:16

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_auto_20190202_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_image',
            field=models.ImageField(blank=True, null=True, upload_to=products.models.image_upload_to_category),
        ),
    ]
