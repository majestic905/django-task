# Generated by Django 4.0.2 on 2022-02-21 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.IntegerField(unique=True)),
                ('title', models.CharField(max_length=200)),
                ('users_count', models.IntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True))
            ],
        ),
    ]
