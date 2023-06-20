"""Events for the VK Teams Connector."""
from opsdroid import events

class Sticker(events.Event):
    """Event class that triggers when a sticker is sent."""

    def __init__(self, file_id, *args, **kwargs):
        """Contain some attributes that you can access.

        - ``file_id`` - id of the sticker file
        """
        super().__init__(*args, **kwargs)
        self.file_id = file_id


class Mention(events.Event):
    """Event class that triggers when a mention is sent."""

    def __init__(self, mentioned_user_id, *args, **kwargs):
        """Contain some attributes that you can access.

        - ``mentioned_user_id`` - id of the mentioned user
        """
        super().__init__(*args, **kwargs)
        self.mentioned_user_id = mentioned_user_id


class Voice(events.Event):
    """Event class that triggers when a voice message is sent."""

    def __init__(self, file_id, *args, **kwargs):
        """Contain some attributes that you can access.

        - ``file_id`` - id of the audio message voice file
        """
        super().__init__(*args, **kwargs)
        self.file_id = file_id


class File(events.Event):
    """Event class that triggers when a file is sent."""

    def __init__(self, file_id, caption, *args, **kwargs):
        """Contain some attributes that you can access.

        - ``file_id`` - id of the file
        - ``caption`` - caption of the file
        - ``type`` - image, file
        """
        super().__init__(*args, **kwargs)
        self.file_id = file_id
        self.caption = caption
        self.type = type


class Forward(events.Event):
    """Event class that triggers when a forward is sent."""

    def __init__(self, message, *args, **kwargs):
        """Contain some attributes that you can access.

        - ``message`` - The Message object

        """
        super().__init__(*args, **kwargs)
        self.message = message
