# Generated by Django 4.0.6 on 2022-08-02 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0004_auto_20211018_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='sms',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='sms',
            name='other_recipients',
            field=models.ManyToManyField(blank=True, related_name='received_sms', to='messaging.contact'),
        ),
    ]
