from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps as django_apps
from prettytable import PrettyTable


class Command(BaseCommand):
    help = "Retrieves the top scorers for each category"

    def add_arguments(self, parser):
        parser.add_argument(
            "--n",
            type=int,
            default=3,
            help="Specifies the number of top scorers to select from each category.",
        )

    def handle(self, *args, **options):
        # TODO: add CLI list option to select which categories
        criteria = settings.LIVE_JUDGE_CRITERIA
        num_top_scorers = options["n"]

        # TODO: add this to a utils file to avoid repeat code (preparedevpost):
        Project = django_apps.get_model("judge", "project")

        table = PrettyTable(
            field_names=["Category", "Project Name", "Mean"],
            header=True,
        )

        for criterion_index, (criterion_id, criterion_label) in enumerate(
            criteria.items()
        ):
            sorted_projects = Project.objects.order_by(f"-means__{criterion_index}")
            for top_scorer in sorted_projects[:num_top_scorers]:
                table.add_row(
                    [
                        criterion_label,
                        top_scorer.name,
                        top_scorer.means[criterion_index],
                    ]
                )
        self.stdout.write(table.get_string())
