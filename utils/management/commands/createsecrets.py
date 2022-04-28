from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from django.conf import settings


class Command(BaseCommand):
    help = "Updates Docker secrets with production-ready values"

    def handle(self, **options):
        secrets_dir = settings.BASE_DIR / "compose" / "secrets"

        if (settings.BASE_DIR / ".env").exists():
            from sys import stderr, exit

            # Deleting `.env` is not actually necessary for this
            # command, but it is necessary for Docker Compose secrets:
            print(
                "Detected `.env` file. Please delete this file and then re-run this command.",
                file=stderr,
            )
            exit(1)

        prod_secrets_dir = secrets_dir / "production"

        secret_key_file = prod_secrets_dir / "secret_key.txt"
        if not secret_key_file.exists():
            with secret_key_file.open(mode="wt") as f:
                f.write(get_random_secret_key())

        django_superuser_username_file = (
            prod_secrets_dir / "django_superuser_username.txt"
        )
        if not django_superuser_username_file.exists():
            with django_superuser_username_file.open(mode="wt") as f:
                f.write("live_admin")
        django_superuser_password_file = (
            prod_secrets_dir / "django_superuser_password.txt"
        )
        if not django_superuser_password_file.exists():
            with django_superuser_password_file.open(mode="wt") as f:
                # TODO: make it clear that users who run this command should check
                # the ./compose/secrets/production/django_superuser_password.txt
                # file contents so they know the password.
                f.write(get_random_secret_key())
        django_superuser_email_file = prod_secrets_dir / "django_superuser_email.txt"
        if not django_superuser_email_file.exists():
            with django_superuser_email_file.open(mode="wt") as f:
                f.write("sumanth@hacktj.org")

        postgres_password_file = prod_secrets_dir / "postgres_password.txt"
        if not postgres_password_file.exists():
            with postgres_password_file.open(mode="wt") as f:
                f.write(get_random_secret_key())
        postgres_user_file = prod_secrets_dir / "postgres_user.txt"
        if not postgres_user_file.exists():
            with postgres_user_file.open(mode="wt") as f:
                f.write("live_postgres")
        postgres_db_file = prod_secrets_dir / "postgres_db.txt"
        if not postgres_db_file.exists():
            with postgres_db_file.open(mode="wt") as f:
                f.write("hacktj_live")
