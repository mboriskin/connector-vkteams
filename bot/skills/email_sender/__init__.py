import smtplib
import ssl
import re

from opsdroid.skill import Skill
from opsdroid.matchers import match_regex
from opsdroid.constraints import constrain_connectors
from opsdroid.events import Reply, File


class SendEmailSkill(Skill):

    @match_regex(r'send_email', matching_condition="fullmatch")
    async def send_email(self, message):

        if not isinstance(message, Reply):
            await message.respond("Сделайте реплай на сообщение, "
                                  "которое хотите переслать на email")
            return

        message_for_email = f"\n{message.linked_event.user_id}:\n\n" \
                            f"{message.linked_event.text}\n\n"

        if message_for_email:
            send_email(to=["your.real.email@mail.ru"],
                       subject=f"Сообщение из {message.connector.name} (opsdroid)",
                       text=message_for_email)
            await message.respond(f"Сообщение переслано на email")
        else:
            await message.respond("Сообщение для пересылки не содержит текста")


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
            send_email(to=["your.real.email@mail.ru"],
                       subject=f"Сообщение из Slack (opsdroid)",
                       text=remove_emoji(message_for_email))
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
