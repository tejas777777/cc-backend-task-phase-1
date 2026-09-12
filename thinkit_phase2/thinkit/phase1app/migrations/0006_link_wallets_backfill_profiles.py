from django.db import migrations


def link_wallets_and_backfill_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Wallet = apps.get_model('phase1app', 'Wallet')
    Profile = apps.get_model('phase1app', 'Profile')

    for wallet in Wallet.objects.all():
        user = User.objects.filter(username=wallet.username).first()
        if user is None:
            # Dev/test wallet row with no matching real user - nothing to link it to.
            wallet.delete()
            continue
        wallet.user = user
        wallet.save(update_fields=['user'])

    for user in User.objects.all():
        Profile.objects.get_or_create(user=user, defaults={'role': 'buyer'})


class Migration(migrations.Migration):

    dependencies = [
        ('phase1app', '0005_wallet_user'),
    ]

    operations = [
        migrations.RunPython(link_wallets_and_backfill_profiles, migrations.RunPython.noop),
    ]
