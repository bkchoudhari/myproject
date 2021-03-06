# Generated by Django 3.0 on 2021-11-29 13:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_wishlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('price', models.IntegerField()),
                ('qty', models.IntegerField(default=1)),
                ('total_price', models.IntegerField()),
                ('cloth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.Cloth')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.User')),
            ],
        ),
    ]
