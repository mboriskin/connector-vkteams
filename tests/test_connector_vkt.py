import logging

import asyncio
import contextlib
import asynctest.mock as amock
import pytest

from vkt_connector import ConnectorVKTeams
from vkt_events import (
    Sticker,
    Mention,
    Voice,
    VKTFile,
    Forward,
)

from opsdroid.events import (
    Message,
    JoinGroup,
    LeaveGroup,
    PinMessage,
    UnpinMessage,
    DeleteMessage,
    Reply,
)

from .test_standard_events import (
    new_message_event,
    new_message_reply,
    new_message_deleted_message,
    new_message_pinned_message,
    new_message_unpinned_message,
    new_message_new_chat_memebrs,
    new_message_left_chat_members,
    new_message_edited_message,
)
from .test_custom_events import (
    new_message_file,
    new_message_voice,
    new_message_forward,
    new_message_mention,
    new_message_sticker,
)

VKTEAMS_BOT_API_ENDPOINT = "https://api.my-company.myteam.mail.ru/bot/v1/"

connector_config = {
    "token": "test:token",
}


def test_init(opsdroid):
    config = {
        "token": "test:token",
        "whitelisted-users": ["my.work.mail@mail.ru"],
        "base-url": "test.com/",
    }

    connector = ConnectorVKTeams(config, opsdroid=opsdroid)

    assert "vkteams" == connector.name
    assert "test:token" == connector.token
    assert ["my.work.mail@mail.ru"] == connector.whitelisted_users
    assert "test.com/" == connector.base_url


def test_init_no_token(opsdroid, caplog):
    connector_config_without_token = {
        "base-url": "test:base-url",
    }
    connector = ConnectorVKTeams(connector_config_without_token, opsdroid=opsdroid)
    caplog.set_level(logging.ERROR)

    assert "vkteams" == connector.name
    assert connector.whitelisted_users is None
    assert "test:base-url" == connector.base_url
    assert "Unable to login: Access token is missing" in caplog.text


def test_init_no_base_url(opsdroid, caplog):
    connector_config_without_base_url = {
        "token": "test:token",
    }
    connector = ConnectorVKTeams(connector_config_without_base_url, opsdroid=opsdroid)
    caplog.set_level(logging.ERROR)

    assert "vkteams" == connector.name
    assert "test:token" == connector.token
    assert None is connector.whitelisted_users


def test_get_user_from_pm(opsdroid):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = new_message_event
    user_id = connector.get_user(response)

    assert "my.work.mail@mail.ru" == user_id


def test_get_user_from_group_chat(opsdroid):
    new_message_event["payload"]["chat"]["chatId"] = "687147040@chat.agent"
    new_message_event["payload"]["chat"]["title"] = "testGroup opsdroid"
    new_message_event["payload"]["chat"]["type"] = "group"

    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    user_id = connector.get_user(new_message_event)

    assert "my.work.mail@mail.ru" == user_id


def test_get_user_from_channel(opsdroid):
    new_message_event["payload"]["chat"]["chatId"] = "687147090@chat.agent"
    new_message_event["payload"]["chat"]["title"] = "testChannel opsdroid"
    new_message_event["payload"]["chat"]["type"] = "channel"

    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    user_id = connector.get_user(new_message_event)

    assert "my.work.mail@mail.ru" == user_id


def test_handle_user_permission_empty_whitelist(opsdroid):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    permission = connector.handle_user_permission(
        "nickname_test", "my.work.mail@mail.ru"
    )

    assert permission is True


def test_handle_user_permission_present_in_white_list(opsdroid):
    config = connector_config
    config["whitelisted-users"] = ["my.work.mail@mail.ru"]
    connector = ConnectorVKTeams(config, opsdroid=opsdroid)

    permission = connector.handle_user_permission(
        new_message_event, "my.work.mail@mail.ru"
    )

    assert permission is True


def test_handle_user_permission_not_empty_white_list(opsdroid):
    config = connector_config
    config["whitelisted-users"] = ["12341234"]
    connector = ConnectorVKTeams(config, opsdroid=opsdroid)

    permission = connector.handle_user_permission("samb", "my.work.mail@mail.ru")

    assert permission is False


def test_build_url(opsdroid):
    config = connector_config
    config["base-url"] = VKTEAMS_BOT_API_ENDPOINT
    connector = ConnectorVKTeams(config, opsdroid=opsdroid)

    method = "events/get"
    url = connector.build_url(method)

    assert url == f"https://{VKTEAMS_BOT_API_ENDPOINT}{method}"


@pytest.mark.asyncio
async def test_connect(opsdroid, caplog):
    caplog.set_level(logging.DEBUG)
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    connect_response = amock.Mock()
    connect_response.status = 200
    connect_response.json = amock.CoroutineMock()
    connect_response.return_value = new_message_event

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("aiohttp.ClientSession.get") as patched_request:
        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(connect_response)

        await connector.connect()
        assert 200 != patched_request.status
        assert "DEBUG" in caplog.text
        assert patched_request.called


@pytest.mark.asyncio
async def test_connect_failure(opsdroid, caplog):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    result = amock.MagicMock()
    result.status = 401

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("aiohttp.ClientSession.get") as patched_request:
        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(result)

        await connector.connect()
        assert "ERROR" in caplog.text


@pytest.mark.asyncio
async def test_parse_message_private(opsdroid):
    connector_config["whitelisted-users"] = ["my.work.mail@mail.ru"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    new_message_event["payload"]["chat"]["chatId"] = "my.work.mail@mail.ru"
    new_message_event["payload"]["chat"]["type"] = "private"

    response = {
        "events": [new_message_event],
        "ok": True,
    }

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_unauthorized(opsdroid):
    connector_config["whitelisted-users"] = ["user", "test"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    new_message_event["payload"]["from"]["userId"] = "my.work.mail@mail.ru"
    new_message_event["payload"]["chat"]["type"] = "private"

    response = {
        "events": [new_message_event],
        "ok": True,
    }

    assert connector.whitelisted_users, ["user", "test"]

    message_text = "У вас нет доступа к взаимодействию с ботом"

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(connector, "send") as mocked_respond:
        await connector._parse_message(response)
        assert mocked_respond.called
        assert mocked_respond.called_with(message_text)


@pytest.mark.asyncio
async def test_parse_message_in_group_unauthorized(opsdroid):
    connector_config["whitelisted-users"] = ["user", "test"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    new_message_event["payload"]["from"]["userId"] = "my.work.mail@mail.ru"
    new_message_event["payload"]["chat"]["type"] = "group"

    response = {
        "events": [new_message_event],
        "ok": True,
    }

    assert connector.whitelisted_users, ["user", "test"]

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(connector, "send") as mocked_respond:
        await connector._parse_message(response)
        assert mocked_respond.called


@pytest.mark.asyncio
async def test_parse_edited_message(opsdroid, caplog):
    caplog.set_level(logging.DEBUG)
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_edited_message],
        "ok": True,
    }

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    mocked_status = amock.CoroutineMock()
    mocked_status.status = 200
    with amock.patch("opsdroid.core.OpsDroid.parse"), amock.patch.object(
        connector, "get_messages_loop"
    ), amock.patch.object(connector.session, "post") as patched_request:
        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(mocked_status)
        assert "editedMessage" == response.get("events", {})[0].get("type", None)

        await connector._parse_message(response)


@pytest.mark.asyncio
async def test_parse_message_unknown_type(opsdroid, caplog):
    caplog.set_level(logging.DEBUG)
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    unknown_type_event = new_message_event
    unknown_type_event["type"] = "unknownType"
    response = {
        "events": [unknown_type_event],
        "ok": True,
    }

    await connector._parse_message(response)
    assert "Ignoring event" in caplog.text


@pytest.mark.asyncio
async def test_parse_message_bad_result(opsdroid, caplog):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    no_event_id_event = {
        "payload": {
            "chat": {"chatId": "my.work.mail@mail.ru", "type": "private"},
            "from": {
                "firstName": "Samuel",
                "lastName": "B",
                "userId": "my.work.mail@mail.ru",
            },
            "msgId": "7158448019745013765",
            "text": "test message 123",
            "timestamp": 1666706060,
        },
        "type": "unknownType",
    }
    response = {
        "events": [no_event_id_event],
        "ok": True,
    }

    await connector._parse_message(response)
    assert "ERROR" in caplog.text


@pytest.mark.asyncio
async def test_get_messages(opsdroid, caplog):
    caplog.set_level(logging.DEBUG)
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    listen_response = amock.Mock()
    listen_response.status = 200
    listen_response.json = amock.CoroutineMock()
    listen_response.return_value = new_message_event

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(
        connector.session, "get"
    ) as patched_request, amock.patch.object(
        connector, "_parse_message"
    ) as mocked_parse_message:
        connector.latest_update = 54
        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(listen_response)

        await connector._get_messages()
        assert patched_request.called
        assert "DEBUG" in caplog.text
        assert mocked_parse_message.called


@pytest.mark.asyncio
async def test_get_messages_failure(opsdroid, caplog):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    listen_response = amock.Mock()
    listen_response.status = 401

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(connector.session, "get") as patched_request:
        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(listen_response)
        await connector._get_messages()
        assert "ERROR" in caplog.text


@pytest.mark.asyncio
async def test_get_messages_loop(opsdroid):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    connector._get_messages = amock.CoroutineMock()
    connector._get_messages.side_effect = Exception()
    with contextlib.suppress(Exception):
        await connector.get_messages_loop()


@pytest.mark.asyncio
async def test_respond(opsdroid, caplog):
    caplog.set_level(logging.DEBUG)
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    post_response = amock.Mock()
    post_response.status = 200

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(connector.session, "post") as patched_request:
        assert opsdroid.__class__.instances
        test_message = Message(
            text="This is a test",
            user="opsdroid",
            target="my.work.mail@mail.ru",
            connector=connector,
        )

        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(post_response)

        await test_message.respond("Response")
        assert patched_request.called
        assert "DEBUG" in caplog.text


@pytest.mark.asyncio
async def test_respond_failure(opsdroid, caplog):
    caplog.set_level(logging.DEBUG)
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    post_response = amock.Mock()
    post_response.status = 401

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(connector.session, "post") as patched_request:
        assert opsdroid.__class__.instances
        test_message = Message(
            text="This is a test",
            user="opsdroid",
            target="my.work.mail@mail.ru",
            connector=connector,
        )

        patched_request.return_value = asyncio.Future()
        patched_request.return_value.set_result(post_response)

        await test_message.respond("Response")
        assert "DEBUG" in caplog.text


@pytest.mark.asyncio
async def test_listen(opsdroid):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    with amock.patch.object(
        connector.loop, "create_task"
    ) as mocked_task, amock.patch.object(
        connector._closing, "wait"
    ) as mocked_event, amock.patch.object(
        connector, "get_messages_loop"
    ):
        mocked_event.return_value = asyncio.Future()
        mocked_event.return_value.set_result(True)
        mocked_task.return_value = asyncio.Future()

        await connector.listen()
        assert mocked_event.called
        assert mocked_task.called


@pytest.mark.asyncio
async def test_disconnect(opsdroid):
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch.object(connector.session, "close") as mocked_close:
        mocked_close.return_value = asyncio.Future()
        mocked_close.return_value.set_result(True)

        await connector.disconnect()
        assert not connector.listening
        assert connector.session.closed()
        assert connector._closing.set() is None


@pytest.mark.asyncio
async def test_parse_message_sticker(opsdroid):
    connector_config["whitelisted-users"] = ["1234567890"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_sticker],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_sticker
    )
    assert isinstance(parsed_result, Sticker)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_mention(opsdroid):
    connector_config["whitelisted-users"] = ["1234567890"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_mention],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_mention
    )
    assert isinstance(parsed_result, Mention)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_voice(opsdroid):
    connector_config["whitelisted-users"] = ["1234567890"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_voice],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_voice
    )
    assert isinstance(parsed_result, Voice)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_file(opsdroid):
    connector_config["whitelisted-users"] = ["1234567890"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_file],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_file
    )
    assert isinstance(parsed_result, VKTFile)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_forward(opsdroid):
    connector_config["whitelisted-users"] = ["1234567890"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_forward],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_forward
    )
    assert isinstance(parsed_result, Forward)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_reply(opsdroid):
    connector_config["whitelisted-users"] = ["1234567890"]
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_reply],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_reply
    )
    assert isinstance(parsed_result, Reply)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_deleted_message(opsdroid):
    connector_config["whitelisted-users"] = []
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_deleted_message],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_deleted_message
    )
    assert isinstance(parsed_result, DeleteMessage)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_pinned_message(opsdroid):
    connector_config["whitelisted-users"] = []
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_pinned_message],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_pinned_message
    )
    assert isinstance(parsed_result, PinMessage)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_unpinned_message(opsdroid):
    connector_config["whitelisted-users"] = []
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_unpinned_message],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_unpinned_message
    )
    assert isinstance(parsed_result, UnpinMessage)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_new_chat_memebrs(opsdroid):
    connector_config["whitelisted-users"] = []
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_new_chat_memebrs],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_new_chat_memebrs
    )
    assert isinstance(parsed_result, JoinGroup)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called


@pytest.mark.asyncio
async def test_parse_message_left_chat_members(opsdroid):
    connector_config["whitelisted-users"] = []
    connector = ConnectorVKTeams(connector_config, opsdroid=opsdroid)

    response = {
        "events": [new_message_left_chat_members],
        "ok": True,
    }

    parsed_result = await connector.handle_messages(
        user=None, target=None, event_id=None, raw_event=new_message_left_chat_members
    )
    assert isinstance(parsed_result, LeaveGroup)

    with amock.patch("aiohttp.ClientSession") as mocked_session:
        connector.session = mocked_session

    with amock.patch("opsdroid.core.OpsDroid.parse") as mocked_parse:
        await connector._parse_message(response)
        assert mocked_parse.called
