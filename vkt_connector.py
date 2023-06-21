"""A connector for VK Teams"""
import logging
import aiohttp
import asyncio
from voluptuous import Required

from opsdroid.connector import Connector, register_event
from opsdroid.events import (
    Message,
    File,
    EditedMessage,
    JoinGroup,
    LeaveGroup,
    PinMessage,
    UnpinMessage,
    DeleteMessage,
    Reply,
)

from . import vkt_events

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = {
    Required("token"): str,
    "update-interval": float,
    "default-user": str,
    "whitelisted-users": list,
}


class ConnectorVKTeams(Connector):
    """A connector for VK Teams"""

    def __init__(self, config, opsdroid=None):
        """
        Create the connector.
        :param config (dict): configuration settings from the file configuration.yaml.
        :param opsdroid (OpsDroid): An instance of opsdroid.core.
        """
        _LOGGER.debug("Loaded VK Teams Connector")
        super().__init__(config, opsdroid=opsdroid)
        self.name = "vkteams"
        self.opsdroid = opsdroid
        self.latest_update = None
        self.listening = True
        self.base_url = config.get("base-url", None)
        self.default_user = config.get("default-user", None)
        self.default_target = self.default_user
        self.whitelisted_users = config.get("whitelisted-users", None)
        self.update_interval = config.get("update-interval", 1)
        self.session = None
        self._closing = asyncio.Event()
        self.loop = asyncio.get_event_loop()
        try:
            self.token = config["token"]
        except (KeyError, AttributeError):
            _LOGGER.error(
                "Unable to login: Access token is missing. VKT connector will be unavailable."
            )

    @staticmethod
    def get_user(event):
        """
        Get user from response.
        The API response is different depending on how
        the bot is set up and where the message is coming
        from. This method was created to keep if/else
        statements to a minium on _parse_message.
        :param response (str): Response returned by aiohttp.ClientSession.
        """
        user = None

        try:
            if "userId" in event.get("payload", {}).get("from", None):
                user = event["payload"]["from"]["userId"]
        except TypeError:
            pass

        return user

    @staticmethod
    def get_target(event):
        """
        Get user from response.
        The API response is different depending on how
        the bot is set up and where the message is coming
        from. This method was created to keep if/else
        statements to a minium on _parse_message.
        :param response (str): Response returned by aiohttp.ClientSession.
        """
        target = None

        try:
            if "chatId" in event.get("payload", {}).get("chat", None):
                target = event["payload"]["chat"]["chatId"]
        except TypeError:
            pass

        return target

    def handle_user_permission(self, response, user):
        """
        Handle user permissions.
        This will check if the user that tried to talk with
        the bot is allowed to do so.
        """
        if not self.whitelisted_users or user in self.whitelisted_users:
            return True

        return False

    def build_url(self, method):
        """
        Build the url to connect to the API.
        :param method (str): API call end point.
        :return: String that represents the full API url.
        """
        return f"https://{self.base_url}{method}"

    async def connect(self):
        """
        Connect to VK Teams.
        Basically checks if provided token is valid.
        """
        _LOGGER.debug("Connecting to VK Teams.")

        self.session = aiohttp.ClientSession()
        params = {"token": self.token}
        resp = await self.session.get(url=self.build_url("self/get"), params=params)

        if resp.status != 200:
            _LOGGER.error("Unable to connect.")
            _LOGGER.error(f"VK Teams error {resp.status}, {resp.text}.")
        else:
            json = await resp.json()
            _LOGGER.debug(json)
            _LOGGER.debug(f"Connected to VK Teams as {json['nick']}.")

    async def _parse_message(self, response):
        """
        Handle logic to parse a received message.
        Since everyone can send a private message to any user/bot
        in VK Teams, this method allows to set a list of whitelisted
        users that can interact with the bot. If any other user tries
        to interact with the bot the command is not parsed and instead
        the bot will inform that user that he is not allowed to talk
        with the bot.
        We also set self.latest_update to +1 in order to get the next
        available message (or an empty {} if no message has been received
        yet) with the method self._get_messages().
        :param response (dict): Response returned by aiohttp.ClientSession.
        """

        _LOGGER.debug(response)
        try:
            for event in response["events"]:
                _LOGGER.debug(event)
                user = self.get_user(event)
                target = self.get_target(event)
                parsed_event = await self.handle_messages(
                    user=user,
                    target=target,
                    event_id=event.get("eventId"),
                    raw_event=event,
                )
                if parsed_event:
                    if self.handle_user_permission(event, user):
                        await self.opsdroid.parse(parsed_event)
                    else:
                        block_message = Message(
                            text="У вас нет доступа к взаимодействию с ботом",
                            user=user,
                            user_id=user,
                            target=target,
                            connector=self,
                        )
                        await self.send(block_message)
                    self.latest_update = event["eventId"]
                elif "eventId" in event:
                    self.latest_update = event["eventId"]
                    _LOGGER.debug("Ignoring event.")
                else:
                    _LOGGER.error("Unable to parse the event.")
        except BaseException:
            raise

    async def _get_messages(self):
        """
        Connect to the VK Teams API.
        Uses an aiohttp ClientSession to connect to VK Teams API
        and get the latest messages from the chat service.
        The data["lastEventId"] is used to consume every new message, the API
        returns an  int - "update_id" value. In order to get the next
        message this value needs to be increased by 1 the next time
        the API is called. If no new messages exists the API will just
        return an empty {}.
        """
        data = {"token": self.token, "pollTime": 30, "lastEventId": 1}
        if self.latest_update is not None:
            data["lastEventId"] = self.latest_update

        await asyncio.sleep(self.update_interval)
        resp = await self.session.get(self.build_url("events/get"), params=data)

        if resp.status != 200:
            _LOGGER.error(f"VK Teams error {resp.status}, {resp.text}.")
            self.listening = False
        else:
            json = await resp.json()
            await self._parse_message(json)

    async def get_messages_loop(self):
        """
        Listen for and parse new messages.
        The bot will always listen to all events from the server
        The method will sleep asynchronously at the end of
        every loop. The time can either be specified in the
        configuration.yaml with the param update-interval - this
        defaults to 1 second.
        """
        while self.listening:
            await self._get_messages()

    async def listen(self):
        """
        Listen method of the connector.
        Every connector has to implement the listen method. When an
        infinite loop is running, it becomes hard to cancel this task.
        So we are creating a task and set it on a variable, so we can
        cancel the task.
        """
        message_getter = self.loop.create_task(await self.get_messages_loop())
        await self._closing.wait()
        message_getter.cancel()

    async def handle_messages(self, user, target, event_id, raw_event):
        """
        Create OpsDroid events depending on the type of message that we get from VK Teams.
        It only gives us back the file id, sizes, formats and that's it.
        And just log a message in debug mode with the payload and return None,
        if it is an event we can't parse.

        message (dict): The payload received from VK Teams
        user (string): The name of the user that sent the message
        user_id (int): The unique user id from the user that send the message
        update_id (int): The unique id for the parsed_event
        """

        if raw_event.get("type") == "newChatMembers":
            return JoinGroup(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                connector=self,
                raw_event=raw_event,
            )

        if raw_event.get("type") == "leftChatMembers":
            return LeaveGroup(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                connector=self,
                raw_event=raw_event,
            )

        if raw_event.get("type") == "pinnedMessage":
            return PinMessage(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                connector=self,
                raw_event=raw_event,
            )

        if raw_event.get("type") == "unpinnedMessage":
            return UnpinMessage(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                connector=self,
                raw_event=raw_event,
            )

        if raw_event.get("type") == "deletedMessage":
            return DeleteMessage(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                connector=self,
                raw_event=raw_event,
            )

        if raw_event.get("type") == "editedMessage":
            return EditedMessage(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                connector=self,
                raw_event=raw_event,
            )

        message_parts = raw_event.get("payload", {}).get("parts", {})
        if message_parts:
            message_part = message_parts[0]
            if message_part.get("type") == "reply":
                linked_event = None
                replied_message_author = message_part["payload"]["message"]["from"][
                    "userId"
                ]
                if message_part.get("payload", {}).get("message", {}).get("parts", {}):
                    linked_event = await self._handle_vkt_events(
                        first_part=message_part["payload"]["message"]["parts"][0],
                        raw_event=message_part,
                        user=replied_message_author,
                    )
                elif message_part.get("payload", {}).get("message", {}):
                    linked_event = Message(
                        text=message_part["payload"]["message"]["text"],
                        user=f"@[{replied_message_author}]",
                        user_id=replied_message_author,
                        target=target,
                        connector=self,
                        raw_event=message_part,
                        event_id=event_id,
                    )

                parsed_event = Reply(
                    text=raw_event["payload"]["text"],
                    user=f"@[{user}]",
                    user_id=user,
                    event_id=event_id,
                    linked_event=linked_event,
                    target=target,
                    connector=self,
                    raw_event=raw_event,
                )
                _LOGGER.debug(f"Parsed event: {parsed_event}")
                return parsed_event

        if raw_event.get("type") == "newMessage":
            if raw_event.get("payload", {}).get("parts", {}):
                parsed_event = await self._handle_vkt_events(
                    first_part=raw_event["payload"]["parts"][0],
                    raw_event=raw_event,
                    user=user,
                    target=target,
                    event_id=event_id,
                )
                _LOGGER.debug(f"Parsed event: {parsed_event}")
            else:
                return Message(
                    text=raw_event["payload"]["text"],
                    user=f"@[{user}]",
                    user_id=user,
                    target=target,
                    connector=self,
                    raw_event=raw_event,
                    event_id=event_id,
                )
            return parsed_event

        _LOGGER.debug(
            f"Received unparsable parsed_event from VK Teams. Payload: {raw_event}"
        )

    async def _handle_vkt_events(
        self, first_part, raw_event, user=None, target=None, event_id=None
    ):
        if first_part.get("type", "") == "sticker":
            return vkt_events.Sticker(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                file_id=first_part["payload"]["fileId"],
                connector=self,
                raw_event=raw_event,
            )

        if first_part.get("type", "") == "mention":
            return vkt_events.Mention(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                mentioned_user_id=first_part["payload"]["userId"],
                connector=self,
                raw_event=raw_event,
            )

        if first_part.get("type", "") == "voice":
            return vkt_events.Voice(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                file_id=first_part["payload"]["fileId"],
                connector=self,
                raw_event=raw_event,
            )

        if first_part.get("type", "") == "file":
            return vkt_events.VKTFile(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                file_id=first_part["payload"]["fileId"],
                caption=first_part["payload"]["caption"],
                type=first_part["payload"]["type"],
                connector=self,
                raw_event=raw_event,
            )

        if first_part.get("type", "") == "forward":
            return vkt_events.Forward(
                user=f"@[{user}]",
                user_id=user,
                event_id=event_id,
                target=target,
                message=Message(
                    text=raw_event["payload"]["text"],
                    user=f"@[{first_part['payload']['message']['from']['userId']}]",
                    user_id=first_part["payload"]["message"]["from"]["userId"],
                    connector=self,
                    raw_event=first_part,
                ),
                connector=self,
                raw_event=raw_event,
            )

    @register_event(Message)
    async def send_message(self, message):
        """
        Respond with a message.
        :param message: An instance of Message.
        """
        _LOGGER.debug(
            f"Responding with: '{message.text}' at target: '{message.target}'"
        )

        data = dict()
        data["token"] = self.token
        data["chatId"] = message.target
        data["text"] = message.text
        resp = await self.session.post(self.build_url("messages/sendText"), data=data)
        if resp.status == 200:
            _LOGGER.debug("Successfully responded.")
        else:
            _LOGGER.error("Unable to respond.")

    @register_event(File)
    async def send_file(self, file_event):
        """
        Respond with a file.
        :param file_event: An instance of File.
        """
        data = aiohttp.FormData()
        data.add_field("token", str(self.token))
        data.add_field(
            "chatId", str(file_event.target), content_type="multipart/form-data"
        )
        data.add_field(
            "file",
            await file_event.get_file_bytes(),
            content_type="multipart/form-data",
        )

        async with aiohttp.ClientSession() as session:
            resp = await session.post(self.build_url("messages/sendFile"), data=data)
            _LOGGER.debug(f"Response is: {resp}")
            if resp.status == 200:
                _LOGGER.debug(f"Sent {file_event.name} file successfully.")
            else:
                _LOGGER.debug(f"Unable to send file - Status Code {resp.status}.")

    async def disconnect(self):
        """
        Disconnect from VK Teams.
        Stops the infinite loop found in self._listen(), closes
        aiohttp session.
        """
        self.listening = False
        self._closing.set()
        await self.session.close()
