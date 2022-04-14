from django.core.management.base import BaseCommand
from allauth.account import app_settings as allauth_account_settings
from django.contrib.auth import get_user_model
from judge.controllers import choose_next


class Command(BaseCommand):
    help = "Re-assigns a judge to a new project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pk",
            type=str,
            help="Specifies the primary key of the judge's user account.",
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Specifies the username of the judge's user account.",
        )
        if allauth_account_settings.UNIQUE_EMAIL:  # ACCOUNT_UNIQUE_EMAIL
            parser.add_argument(
                "--email",
                type=str,
                help="Specifies the email of the judge's user account.",
            )

    def handle(self, *args, **options):
        fields = {}
        if options["pk"] is not None:
            fields["pk"] = options["pk"]
        if options["username"] is not None:
            fields["username"] = options["username"]
        if options["email"] is not None:
            fields["email"] = options["email"]
        if len(fields) == 0:
            self.parser.error(
                "At least one argument must be passed to identify the judge."
            )

        judge = (
            get_user_model()
            .objects.select_related("annotator")
            .get(groups__name="judge", **fields)
        )
        old_project = judge.annotator.current
        judge.annotator.ignore.add(judge.annotator.current)
        new_project = choose_next(judge.annotator)
        assert new_project != old_project

        judge.annotator.update_current(new_project)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully re-assigned judge {judge} from project {old_project} to project {new_project}"
            )
        )
