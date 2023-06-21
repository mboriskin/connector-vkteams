new_message_sticker = {
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
                "type": "sticker",
                "payload": {"fileId": "2IWuJzaNWCJZxJWCvZhDYuJ5XDsr7hU"},
            }
        ],
    },
}


new_message_mention = {
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
                "type": "mention",
                "payload": {
                    "userId": "1234567890",
                    "firstName": "Name",
                    "lastName": "SurName",
                },
            }
        ],
    },
}


new_message_voice = {
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
            {"type": "voice", "payload": {"fileId": "IdjUEXuGdNhLKUfD5rvkE03IOax54cD"}}
        ],
    },
}


new_message_file = {
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
                "type": "file",
                "payload": {
                    "fileId": "ZhSnMuaOmF7FRez2jGWuQs5zGZwlLa0",
                    "type": "image",
                    "caption": "Last weekend trip",
                    "format": {
                        "bold": [{"offset": 0, "length": 1}],
                        "italic": [{"offset": 0, "length": 1}],
                        "underline": [{"offset": 0, "length": 1}],
                        "strikethrough": [{"offset": 0, "length": 1}],
                        "link": [
                            {"offset": 0, "length": 1, "url": "https://example.com/"}
                        ],
                        "mention": [{"offset": 0, "length": 1}],
                        "inline_code": [{"offset": 0, "length": 1}],
                        "pre": [{"offset": 0, "length": 1, "code": "string"}],
                        "ordered_list": [{"offset": 0, "length": 1}],
                        "unordered_list": [{"offset": 0, "length": 1}],
                        "quote": [{"offset": 0, "length": 1}],
                    },
                },
            }
        ],
    },
}


new_message_forward = {
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
                "type": "forward",
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
