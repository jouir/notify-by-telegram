# notify-by-telegram
Send Nagios notifications to a Telegram channel.


## Telegram bot

This [tutorial](https://takersplace.de/2019/12/19/telegram-notifications-with-nagios/) explains how to create a Telegram bot. You'll need the *chat_id* and *auth_key* for the next section.

## Installation

_This guide has been written for [Debian](https://www.debian.org/). Some commands might slightly change depending on your distribution._

Clone the repository:
```
git clone https://github.com/jouir/notify-by-telegram.git
sudo cp -p notify-by-telegram.py /usr/lib/nagios/plugins/notify-by-telegram.py
sudo chmod 755 /usr/lib/nagios/plugins/notify-by-telegram.py
sudo chown root:root /usr/lib/nagios/plugins/notify-by-telegram.py
```

Install dependencies using the package manager:
```
sudo apt install python3-jinja2 python3-requests
```

## Configuration

Copy and update the configuration file example:
```
sudo cp -p config.json.example /etc/nagios/telegram.json
sudo chmod 640 root:nagios /etc/nagios/telegram.json
```

Add Nagios configurations:
```
sudo cp -p nagios.cfg /etc/nagios4/conf.d/telegram.cfg
```

Ensure Nagios reads the configuration file:
```
grep cfg_dir=/etc/nagios4/conf.d /etc/nagios4/nagios.cfg
```

Then reload service:
```
systemctl reload nagios4
```

## Logs

Errors logs can be set with the `--logfile` argument.

Example:
```
tail -f /var/log/nagios4/telegram.log
```

Log level can be raised using `--verbose` or even more with `--debug` arguments.
