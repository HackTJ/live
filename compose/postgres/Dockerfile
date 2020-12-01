FROM postgres:13.1-alpine

# add backup scripts
COPY backup.sh /usr/local/bin/backup
COPY restore.sh /usr/local/bin/restore
COPY list-backups.sh /usr/local/bin/list-backups

# make them executable
RUN chmod +x /usr/local/bin/restore /usr/local/bin/list-backups /usr/local/bin/backup
