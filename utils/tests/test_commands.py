from io import StringIO
from django.core.management import call_command
from django.test import TestCase


class CreateSecretsTest(TestCase):
    def test_exclude_all(self):
        out = StringIO()
        call_command(
            "createsecrets",
            exclude=["secret", "superuser", "sendgrid", "postgres"],
            stdout=out,
        )
        self.assertEqual(out.getvalue(), "\n")

    def test_exclude_none(self):
        out = StringIO()
        call_command(
            "createsecrets",
            stdout=out,
        )
        command_output = out.getvalue()
        self.assertIn("SECRET_KEY=", command_output)
        self.assertIn("DJANGO_SUPERUSER_USERNAME=", command_output)
        self.assertIn("DJANGO_SUPERUSER_PASSWORD=", command_output)
        self.assertIn("DJANGO_SUPERUSER_EMAIL=", command_output)
        self.assertIn("SENDGRID_API_KEY=", command_output)
        self.assertIn("POSTGRES_PASSWORD=", command_output)
        self.assertIn("POSTGRES_USER=", command_output)
        self.assertIn("POSTGRES_DB=", command_output)
        self.assertIn("POSTGRES_INITDB_ARGS=", command_output)
        self.assertIn("POSTGRES_HOST_AUTH_METHOD=", command_output)
