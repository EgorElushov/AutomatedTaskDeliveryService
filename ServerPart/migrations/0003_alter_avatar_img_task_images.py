# Generated by Django 4.2.1 on 2023-05-09 09:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ServerPart', '0002_alter_avatar_img_userip_userinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='img',
            field=models.ImageField(default='../static/img/default.png', upload_to='pictures/'),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date_created', models.DateTimeField()),
                ('img_amount', models.IntegerField(default=1)),
                ('description', models.TextField(max_length=100, null=True)),
                ('deadline', models.DateTimeField(null=True)),
                ('author', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='pictures/')),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ServerPart.task')),
            ],
        ),
    ]
