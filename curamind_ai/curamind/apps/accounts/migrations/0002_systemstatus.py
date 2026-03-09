# Generated manually to add SystemStatus singleton

from django.db import migrations, models


def create_initial_status(apps, schema_editor):
    SystemStatus = apps.get_model('accounts', 'SystemStatus')
    # ensure one record exists
    if not SystemStatus.objects.exists():
        SystemStatus.objects.create(is_online=True, maintenance_mode=False)


def remove_initial_status(apps, schema_editor):
    SystemStatus = apps.get_model('accounts', 'SystemStatus')
    SystemStatus.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_online', models.BooleanField(default=True)),
                ('maintenance_mode', models.BooleanField(default=False)),
            ],
        ),
        migrations.RunPython(create_initial_status, remove_initial_status),
    ]
