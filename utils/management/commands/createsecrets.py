from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = "Outputs a production-ready dotenv file containing secret keys"

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--exclude",
            action="append",
            default=[],
            help="A group of environment variables to exclude "
            "(use multiple --exclude to exclude multiple group). "
            "Must be one of: ['secret', 'superuser', 'sendgrid', 'postgres'].",
        )
        parser.add_argument(
            "-o", "--output", help="Specifies file to which the output is written."
        )

    def handle(self, *args, **options):
        exclude = options["exclude"]

        secrets = []
        if "secret" not in exclude:
            SECRET_KEY = get_random_secret_key()
            secrets.append(f"SECRET_KEY='{SECRET_KEY}'")
            secrets.append("")
        if "superuser" not in exclude:
            DJANGO_SUPERUSER_USERNAME = "live_admin"
            DJANGO_SUPERUSER_PASSWORD = "admin-secret"
            DJANGO_SUPERUSER_EMAIL = "sumanth@hacktj.org"
            secrets.append(f"DJANGO_SUPERUSER_USERNAME='{DJANGO_SUPERUSER_USERNAME}'")
            secrets.append(f"DJANGO_SUPERUSER_PASSWORD='{DJANGO_SUPERUSER_PASSWORD}'")
            secrets.append(f"DJANGO_SUPERUSER_EMAIL='{DJANGO_SUPERUSER_EMAIL}'")
            secrets.append("")
        if "sendgrid" not in exclude:
            SENDGRID_API_KEY = "SG.KEY"
            secrets.append(f"SENDGRID_API_KEY='{SENDGRID_API_KEY}'")
            secrets.append("")
        if "postgres" not in exclude:
            POSTGRES_PASSWORD = get_random_secret_key()
            POSTGRES_USER = "live_admin"
            POSTGRES_DB = "hacktj_live"
            POSTGRES_INITDB_ARGS = (
                "--auth-host=scram-sha-256 --auth-local=scram-sha-256 "
                "--data-checksums"
            )
            POSTGRES_HOST_AUTH_METHOD = "scram-sha-256"
            secrets.append(f"POSTGRES_PASSWORD='{POSTGRES_PASSWORD}'")
            secrets.append(f"POSTGRES_USER='{POSTGRES_USER}'")
            secrets.append(f"POSTGRES_DB='{POSTGRES_DB}'")
            secrets.append(f"POSTGRES_INITDB_ARGS='{POSTGRES_INITDB_ARGS}'")
            secrets.append(f"POSTGRES_HOST_AUTH_METHOD='{POSTGRES_HOST_AUTH_METHOD}'")
            secrets.append("")

        secrets_data = "\n".join(secrets).rstrip()

        if options.get("output"):
            with open(options["output"], "wt") as output_file:
                output_file.write(secrets_data)
        else:
            self.stdout.write(secrets_data)
