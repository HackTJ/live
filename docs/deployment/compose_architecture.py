from diagrams import Diagram, Cluster
from diagrams.saas.cdn import Cloudflare
from diagrams.onprem.network import Nginx
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL  # Postgresql
from diagrams.onprem.inmemory import Memcached, Redis
from diagrams.programming.framework import Django


with Diagram("Self Hosted", show=False):
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
