new_message_event = {
    "eventId": 1,
    "payload": {
        "chat": {"chatId": "my.work.mail@mail.ru", "type": "private"},
        "from": {
            "firstName": "Samuel",
            "lastName": "B",
            "userId": "my.work.mail@mail.ru",
        },
        "msgId": "12345678901234567890",
        "text": "123 text",
        "timestamp": 1666609676,
    },
    "type": "newMessage",
}


new_message_reply = {
    "eventId": 1,
    "type": "newMessage",
    "payload": {
        "msgId": "57883346846815032",
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "channel",
            "title": "The best channel",
        },
        "from": {"userId": "1234567890", "firstName": "Name", "lastName": "SurName"},
        "timestamp": 1546290000,
        "text": "Hello!",
        "format": {
            "bold": [{"offset": 0, "length": 1}],
            "italic": [{"offset": 0, "length": 1}],
            "underline": [{"offset": 0, "length": 1}],
            "strikethrough": [{"offset": 0, "length": 1}],
            "link": [{"offset": 0, "length": 1, "url": "https://example.com/"}],
            "mention": [{"offset": 0, "length": 1}],
            "inline_code": [{"offset": 0, "length": 1}],
            "pre": [{"offset": 0, "length": 1, "code": "string"}],
            "ordered_list": [{"offset": 0, "length": 1}],
            "unordered_list": [{"offset": 0, "length": 1}],
            "quote": [{"offset": 0, "length": 1}],
        },
        "parts": [
            {
                "type": "reply",
                "payload": {
                    "message": {
                        "from": {
                            "firstName": "Name",
                            "lastName": "SurName",
                            "userId": "1234567890",
                        },
                        "msgId": "6724238139063271643",
                        "text": "some text",
                        "format": {
                            "bold": [{"offset": 0, "length": 1}],
                            "italic": [{"offset": 0, "length": 1}],
                            "underline": [{"offset": 0, "length": 1}],
                            "strikethrough": [{"offset": 0, "length": 1}],
                            "link": [
                                {
                                    "offset": 0,
                                    "length": 1,
                                    "url": "https://example.com/",
                                }
                            ],
                            "mention": [{"offset": 0, "length": 1}],
                            "inline_code": [{"offset": 0, "length": 1}],
                            "pre": [{"offset": 0, "length": 1, "code": "string"}],
                            "ordered_list": [{"offset": 0, "length": 1}],
                            "unordered_list": [{"offset": 0, "length": 1}],
                            "quote": [{"offset": 0, "length": 1}],
                        },
                        "timestamp": 1565608694,
                    }
                },
            }
        ],
    },
}


new_message_edited_message = {
    "eventId": 2,
    "type": "editedMessage",
    "payload": {
        "msgId": "57883346846815032",
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "channel",
            "title": "The best channel",
        },
        "from": {"userId": "1234567890", "firstName": "Name", "lastName": "SurName"},
        "timestamp": 1546290000,
        "text": "Hello!",
        "format": {
            "bold": [{"offset": 0, "length": 1}],
            "italic": [{"offset": 0, "length": 1}],
            "underline": [{"offset": 0, "length": 1}],
            "strikethrough": [{"offset": 0, "length": 1}],
            "link": [{"offset": 0, "length": 1, "url": "https://example.com/"}],
            "mention": [{"offset": 0, "length": 1}],
            "inline_code": [{"offset": 0, "length": 1}],
            "pre": [{"offset": 0, "length": 1, "code": "string"}],
            "ordered_list": [{"offset": 0, "length": 1}],
            "unordered_list": [{"offset": 0, "length": 1}],
            "quote": [{"offset": 0, "length": 1}],
        },
        "editedTimestamp": 1546290099,
    },
}


new_message_deleted_message = {
    "eventId": 3,
    "type": "deletedMessage",
    "payload": {
        "msgId": "57883346846815032",
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "channel",
            "title": "The best channel",
        },
        "timestamp": 1546290000,
    },
}


new_message_pinned_message = {
    "eventId": 4,
    "type": "pinnedMessage",
    "payload": {
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "group",
            "title": "The best group",
        },
        "from": {"userId": "9876543210", "firstName": "Name", "lastName": "SurName"},
        "msgId": "6720509406122810315",
        "text": "Some important information!",
        "format": {
            "bold": [{"offset": 0, "length": 1}],
            "italic": [{"offset": 0, "length": 1}],
            "underline": [{"offset": 0, "length": 1}],
            "strikethrough": [{"offset": 0, "length": 1}],
            "link": [{"offset": 0, "length": 1, "url": "https://example.com/"}],
            "mention": [{"offset": 0, "length": 1}],
            "inline_code": [{"offset": 0, "length": 1}],
            "pre": [{"offset": 0, "length": 1, "code": "string"}],
            "ordered_list": [{"offset": 0, "length": 1}],
            "unordered_list": [{"offset": 0, "length": 1}],
            "quote": [{"offset": 0, "length": 1}],
        },
        "timestamp": 1564740530,
    },
}


new_message_unpinned_message = {
    "eventId": 5,
    "type": "unpinnedMessage",
    "payload": {
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "group",
            "title": "The best group",
        },
        "msgId": "6720509406122810315",
        "timestamp": 1564740530,
    },
}


new_message_new_chat_memebrs = {
    "eventId": 6,
    "type": "newChatMembers",
    "payload": {
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "group",
            "title": "The best group",
        },
        "newMembers": [
            {"userId": "1234567890", "firstName": "Name", "lastName": "SurName"}
        ],
        "addedBy": {"userId": "9876543210", "firstName": "Name", "lastName": "SurName"},
    },
}


new_message_left_chat_members = {
    "eventId": 7,
    "type": "leftChatMembers",
    "payload": {
        "chat": {
            "chatId": "681869378@chat.agent",
            "type": "group",
            "title": "The best group",
        },
        "leftMembers": [
            {"userId": "1234567890", "firstName": "Name", "lastName": "SurName"}
        ],
        "removedBy": {
            "userId": "9876543210",
            "firstName": "Name",
            "lastName": "SurName",
        },
    },
}
