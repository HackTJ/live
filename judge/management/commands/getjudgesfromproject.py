from django.core.management.base import BaseCommand
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = "Retrieves the list of judges that have viewed a project"

    def add_arguments(self, parser):
        self.parser = parser
        parser.add_argument(
            "--pk",
            type=str,
            help="Specifies the primary key for the project.",
        )
        parser.add_argument(
            "--link",
            type=str,
            help="Specifies the link to the project's Devpost.",
        )

    def handle(self, *args, **options):
        fields = {}
        if options["pk"] is not None:
            fields["pk"] = options["pk"]
        if options["link"] is not None:
            fields["link"] = options["link"]
        if len(fields) == 0:
            self.parser.error(
                "At least one argument must be passed to identify the project."
            )

        Project = django_apps.get_model("judge", "project")

        try:
            project = Project.objects.prefetch_related("annotator_viewed__judge").get(
                **fields
            )
        except ObjectDoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"No corresponding project for `{fields}`")
            )
        else:
            # `project.annotator_viewed.values('judge')` only returns the primary keys of each judge:
            judges = project.annotator_viewed.all()

            self.stdout.write(f'Project "{project}" has been viewed by {judges}')
