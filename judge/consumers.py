import logging
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from judge.models import Project

# Get an instance of a logger
logger = logging.getLogger(__name__)


@database_sync_to_async
def get_project(project_id):
    if Project.objects.filter(id=project_id).exists():
        return Project.objects.get(id=project_id)
    else:
        logger.error(f"UNABLE TO GET PROJECT WITH ID {project_id}")


class VoteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("judge", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("judge", self.channel_name)

    async def recieve(self, text_data):
        data = json.loads(text_data)
        command = data.pop("command")

        await self.channel_layer.group_send("judge", {"type": command, "data": data})


class ScoreboardUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("scoreboard", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("scoreboard", self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.pop("command")

        await self.channel_layer.group_send(
            "scoreboard",
            {
                "type": command,
                "data": data,
            },
        )

    async def delete_project(self, event):
        data = event["data"]

        project = await get_project(data["projectId"])
        logger.info(f"DELETING PROJECT {project}")
        if project:  # else, there was an error that should be logged
            # TODO: depending on how we implement models, we may want to set
            # keep_parents to False
            project.delete(keep_parents=True)

        self.send(text_data=json.dumps(data))

    async def edit_project_metadata(self, data):
        self.channel_layer.group_send(
            "scoreboard",
            {
                "type": "edit_project_metadata_",
                "data": data,
            },
        )
        project = await get_project(data["projectId"])
        logger.info(
            f"SETTING ATTRIBUTE {data['changedKey']} "
            f"TO {data['newValue']} FOR PROJECT {project.name}"
        )

    async def edit_project_metadata_(self, event):
        data = event["data"]
        self.send(text_data=json.dumps(data))
