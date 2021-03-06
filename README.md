# notify-by-telegram
Send Nagios notifications to a [Telegram Messenger](https://telegram.org/) channel.


## Telegram bot

This [tutorial](https://takersplace.de/2019/12/19/telegram-notifications-with-nagios/) explains how to create a Telegram bot. You'll need the `chat_id` and `auth_key` for the next section.

## Installation

_This guide has been written for [Debian](https://www.debian.org/). Some commands might slightly change depending on your distribution._

Clone the repository:
```
git clone https://github.com/jouir/notify-by-telegram.git /opt/notify-by-telegram
```

Install dependencies using pip:
```
pip install -r requirements.txt
```

Or via the package manager:
```
sudo apt install python3-jinja2 python3-requests python3-jsonschema
```

## Configuration

Copy and update the configuration file example:
```
cp -p config.example.json telegram.json
vim telegram.json
sudo mv telegram.json /etc/nagios4/telegram.json
sudo chown root:nagios /etc/nagios4/telegram.json
sudo chmod 640 /etc/nagios4/telegram.json
```

Ensure Nagios reads the configuration file:
```
echo "cfg_file=/opt/notify-by-telegram/nagios.cfg" >> /etc/nagios4/nagios.cfg
```

Then reload service:
```
systemctl reload nagios4
```

## Configuration file

Format used is JSON with the following keys:

* `chat_id`: where to send message on Telegram
* `auth_key`: key used to authenticate on Telegram
* `host_template` (optional): path to Markdown template file used for sending host notifications
* `service_template` (optional): path to Markdown template file used for sending service notifications

## Logging

Errors logs can be set with the `--logfile` argument.

Example:
```
tail -f /var/log/nagios4/telegram.log
```

Log level can be raised using `--verbose` or even more with `--debug` arguments.


## Message format

`notify-by-telegram` script uses the `MarkdownV2` format to generate Telegram messages.

[Jinja](https://jinja.palletsprojects.com) is used for templating (eg. replace `{{host_name}}` placeholders by the value submitted by Nagios).

Default **host** and **service** templates can be found in the [templates](templates) directory.

They can be overriden in the configuration file:

```json
{
  "host_template": "/etc/nagios4/host.md.j2",
  "service_template": "/etc/nagios4/service.md.j2"
}
```

Both options are optional.

### Host variables

Variables replaced in the host template:
* `notification_type` (= `$NOTIFICATIONTYPE$`)
* `host_name` (= `$HOSTNAME$`)
* `host_state` (= `$HOSTSTATE$`)
* `host_address` (= `$HOSTADDRESS$`)
* `host_output` (= `$HOSTOUTPUT$`)
* `long_date_time` (= `$LONGDATETIME$`)

### Service variables

Variables replaced in the service template:
* `notification_type` (= `$NOTIFICATIONTYPE$`)
* `service_desc` (= `$SERVICEDESC$`)
* `host_alias` (= `$HOSTALIAS$`)
* `host_address` (= `$HOSTADDRESS$`)
* `service_state` (= `$SERVICESTATE$`)
* `long_date_time` (= `$LONGDATETIME$`)
* `service_output` (= `$SERVICEOUTPUT$`)

## How to contribute

Contributions are welcomed! Feel free to update the code and create a pull-request.

Be sure to lint the code before:
```
docker build -t pre-commit .
docker run -it -v $(pwd):/mnt/ --rm pre-commit bash
# cd /mnt/
# pre-commit run --all-files
# exit
```
