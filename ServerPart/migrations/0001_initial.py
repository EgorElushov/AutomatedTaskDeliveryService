# Generated by Django 4.2.1 on 2023-05-08 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(default='../media/pictures/1R2.png', upload_to='pictures/')),
                ('user_id', models.IntegerField()),
            ],
        ),
    ]
