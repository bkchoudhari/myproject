# Generated by Django 3.0 on 2021-11-16 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_cloth_cloth_seller'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cloth',
            old_name='Cloth_brand',
            new_name='cloth_brand',
        ),
        migrations.AlterField(
            model_name='cloth',
            name='cloth_image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
