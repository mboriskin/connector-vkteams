import smtplib
import ssl
import re

from opsdroid.skill import Skill
from opsdroid.matchers import match_regex
from opsdroid.constraints import constrain_connectors


class SendEmailSkill(Skill):

    @match_regex(r'send_email', matching_condition="fullmatch")
    @constrain_connectors(['slack'])
    async def send_email_slack(self, message):
        slack = self.opsdroid.get_connector('slack')
        message_for_email = ""

        thread_ts = message.raw_event.get('thread_ts', None)
        if not thread_ts:
            await message.respond("Сделайте реплай в тред на сообщение, "
                                  "которое хотите переслать на email")
            return

        replied_message = await slack.slack_web_client.conversations_replies(
            channel=message.target, ts=thread_ts
        )
        if replied_message['ok']:
            messages = replied_message['messages']

        thread_start = messages[0]
        users_info = await slack.slack_web_client.users_info(user=thread_start['user'])

        message_for_email += f"{users_info.get('user').get('real_name')}:" \
                             f"\n\n{thread_start['text']}\n\n"

        if message_for_email:
            receiver = "your.real.email@mail.ru"
            send_email(to=[receiver],
                       subject=f"Сообщение из Slack (opsdroid)",
                       text=remove_emoji(message_for_email))
            await message.respond(f"Сообщение переслано на email")
        else:
            await message.respond("Сообщение для пересылки не содержит текста")

    @match_regex(r'send_email', matching_condition="fullmatch")
    @constrain_connectors(['vkteams'])
    async def send_email_vkteams(self, message):
        message_for_email = ""

        event_data = message.raw_event['payload']
        data_parts = event_data.get('parts', [])
        if not data_parts:
            await message.respond("Сделайте реплай на сообщение, "
                                  "которое хотите переслать на email")
            return

        payload_message = data_parts[0]['payload']['message']
        part_msg_from = payload_message['from']
        if "nick" in part_msg_from:
            replied_message_author = part_msg_from['nick']
        else:
            replied_message_author = f"{part_msg_from['firstName']} {part_msg_from['lastName']} " \
                                     f"({part_msg_from['userId']})"

        message_for_email += f"{replied_message_author}:\n\n" \
                             f"{payload_message['text']}\n\n"

        if message_for_email:
            receiver = "your.real.email@mail.ru"
            send_email(to=[receiver],
                       subject=f"Сообщение из VK Teams (opsdroid)",
                       text=message_for_email)
            await message.respond(f"Сообщение переслано на email")
        else:
            await message.respond("Сообщение для пересылки не содержит текста")


def send_email(to, subject, text):
    port = 465  # starttls
    smtp_server = "smtp.mail.ru"
    sender_email = "your.server@mail.ru"
    receiver_email = ''

    for user in to:
        receiver_email += f"{user},"
    ext_application_password = "your_external_application_password"
    message = f"""\
Subject: {subject}
To: {receiver_email}
{text}"""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, ext_application_password)
        server.sendmail(sender_email, to, message.encode("utf8"))


def remove_emoji(text):
    emoji_pattern = r":[a-zA-Z0-9_]+:"
    return re.sub(emoji_pattern, "", text)
