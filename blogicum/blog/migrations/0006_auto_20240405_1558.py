# Generated by Django 3.2.16 on 2024-04-05 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('created_at',)},
        ),
        migrations.RemoveField(
            model_name='comment',
            name='is_published',
        ),
    ]