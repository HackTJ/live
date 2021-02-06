from django.core.management.base import BaseCommand
from sys import stdin, stdout
from pathlib import Path  # safer than argparse.FileType
from json import loads, dumps
from django.contrib.auth.hashers import identify_hasher, make_password
from django.utils.translation import gettext

salt_translated = gettext("salt")


class Command(BaseCommand):
    help = "Removes private information from a fixture file"
    missing_args_message = (
        "No database fixture specified. Please provide the path of exactly "
        "one fixture in the command line."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture_label",
            default="-",
            type=Path,
            help="Fixture label.",
        )
        parser.add_argument(
            "-r",
            "--redact",
            action="append",
            default=["email", "password"],
            choices=["name", "email", "password"],
            help="A group of values to exclude "
            "(use multiple --redact to redact multiple fields). "
            "Must be one of: ['name', 'email', 'password'].",
        )
        parser.add_argument(
            "-o",
            "--output",
            default="-",
            type=Path,
            help="Specifies file to which the output is written.",
        )

    def handle(self, fixture_label, **options):
        output = {}
        with open(fixture_label, "rt") as f:
            output = loads(f.read())
        for model in output[:]:
            if model["model"] == "auth.user":
                # TODO: new CLI choice for superusers?
                if model["fields"]["is_superuser"]:
                    output.remove(model)

                if "name" in options["redact"]:
                    model["fields"]["first_name"] = "REDACTED"
                    model["fields"]["last_name"] = "REDACTED"
                    # TODO: new CLI choice for username?
                    model["fields"]["username"] = "REDACTED"
                if "email" in options["redact"]:
                    model["fields"]["email"] = "REDACTED@REDACTED.com"
                if "password" in options["redact"]:
                    algorithm = identify_hasher(model["fields"]["password"])
                    salt = algorithm.safe_summary(model["fields"]["password"])[
                        salt_translated
                    ]
                    new_password = make_password(
                        "REDACTED", salt=salt, hasher=algorithm
                    )
                    model["fields"]["password"] = new_password
            if model["model"] == "account.emailaddress":
                if "email" in options["redact"]:
                    user_pk = model["fields"]["user"]
                    new_email = f"REDACTED+{user_pk}@REDACTED.com"
                    model["fields"]["email"] = new_email
        with (
            open(options["output"], "w")
            if options["output"] != Path("-")
            else self.stdout
        ) as f:
            f.write(dumps(output))
