from diagrams import Diagram, Cluster
from diagrams.saas.cdn import Cloudflare
from diagrams.onprem.network import Nginx
from diagrams.onprem.database import PostgreSQL  # Postgresql
from diagrams.onprem.inmemory import Memcached, Redis
from diagrams.programming.framework import Django

# from diagrams.onprem.container import Docker


with Diagram(
    "Self Hosted",
    outformat="svg",
    show=False,
    graph_attr={"bgcolor": "transparent"},
) as diagram:
    # Docker("component")
    cloudflare = Cloudflare("Cloudflare")
    with Cluster("VM"):
        nginx = Nginx("NGINX")
        with Cluster("Docker Compose"):
            django = Django("Live")
            django >> [
                PostgreSQL("PostgreSQL"),
                Memcached("Memcached"),
                Redis("Redis"),
            ]
    cloudflare >> nginx >> django

# the resulting SVG contains absolute paths to images that are vendored inside
# of `diagrams`'s source code so we need to inline the logos, as suggested by:
# https://github.com/mingrammer/diagrams/issues/8#issuecomment-633121034
filepath = f"{diagram.filename}.{diagram.outformat}"

with open(filepath, "rt") as file:
    generated_image = file.read()

from scour.scour import scourString as scour_string

with open(filepath, "wt") as file:
    file.write(scour_string(generated_image))
