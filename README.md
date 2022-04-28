# opsdroid connector VK Teams

A connector for [opsdroid](https://github.com/opsdroid/opsdroid) to send messages using [VK Teams](https://teams.vk.com/).

## Requirements

You need to [register a bot](https://myteam.mail.ru/botapi/) on VK Teams and get an api token for it.

## Configuration

```yaml
connectors:
  vkteams:
    # required
    token: "some-token"  # bot token
```
