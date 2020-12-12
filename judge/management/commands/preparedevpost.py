from django.core.management.base import BaseCommand
from django.apps import apps as django_apps
from csv import DictReader as CsvDictReader
from django.conf import settings  # for num_criteria
from django.core import serializers


def get_project_model():
    return django_apps.get_model("judge", "project")


def get_num_criteria():
    return len(settings.LIVE_JUDGE_CRITERIA)


def row_to_project(row, model=None, num_criteria=None):
    model = model or get_project_model()
    num_criteria = num_criteria or get_num_criteria()
    if "Opt-In Prizes" in row:
        # this is the preferred format
        # in the Devpost export, uncheck "Sort the export by opt-in prize"
        prizes = row["Opt-In Prizes"].split(", ") if row["Opt-In Prizes"] else []
    elif "Opt-in prize" in row:
        prizes = [row["Opt-in Prize"]]
    return model(
        name=row["Project Title"],
        # location='',
        # description=row['Plain Description'],  # no one-line description :(
        # description=row['Submission Tagline'],
        tags=prizes,
        link=row["Submission Url"],
        # TODO: don't hard-code defaults for means and variances
        means=[0.0] * num_criteria,
        variances=[1.0] * num_criteria,
        active=row["Project Status"] == "Submitted (Gallery/Visible)",
    )


class Command(BaseCommand):
    help = "Converts a Devpost CSV export to a HackTJ Live fixture"
    missing_args_message = (
        "No Devpost CSV specified. Please provide the path of at least "
        "one CSV in the command line."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "args", metavar="devpost", nargs="+", help="Devpost CSV filepaths."
        )
        parser.add_argument(
            "--format",
            default="json",  # serializers.serialize
            help="Specifies the output serialization format for fixtures.",
        )
        parser.add_argument(
            "--indent",
            type=int,
            help="Specifies the indent level to use when pretty-printing output.",
        )
        parser.add_argument(
            "-o", "--output", help="Specifies file to which the output is written."
        )

    def handle(self, *devpost_files, **options):
        format = options["format"]
        indent = options["indent"]
        output = options["output"]

        Project = get_project_model()
        num_criteria = get_num_criteria()
        projects = []
        for filepath in devpost_files:
            with open(filepath, "rt", newline="") as file:
                reader = CsvDictReader(file)
                for row in reader:
                    project = row_to_project(
                        row, model=Project, num_criteria=num_criteria
                    )
                    projects.append(project)

        self.stdout.ending = None
        progress_output = None
        object_count = 0
        # If outputting to stdout, there is no way to display progress
        if output and self.stdout.isatty():
            progress_output = self.stdout
            object_count = len(projects)
        stream = open(output, "w") if output else None

        serializers.serialize(
            format,
            projects,
            indent=indent,
            stream=stream or self.stdout,
            progress_output=progress_output,
            object_count=object_count,
        )
