# -*- coding: utf-8 -*-
#: Site title
SITE_TITLE = 'Billgate'
#: Site id (for network bar)
SITE_ID = 'billgate'
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
#: Secret key
SECRET_KEY = 'asdssa'
#: Timezone
TIMEZONE = 'Asia/Calcutta'
#: LastUser server
LASTUSER_SERVER = 'https://auth.hasgeek.com'
#: LastUser client id
LASTUSER_CLIENT_ID = ''
#: LastUser client secret
LASTUSER_CLIENT_SECRET = ''
#: Typekit id
TYPEKIT_CODE = 'qhx6vtv'
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
#: MAIL_SERVER : default 'localhost'
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
#: MAIL_USERNAME : default None
#: MAIL_PASSWORD : default None
#: DEFAULT_MAIL_SENDER : default None
MAIL_FAIL_SILENTLY = False
MAIL_SERVER = 'localhost'
DEFAULT_MAIL_SENDER = ('HasGeek', 'bot@hasgeek.com')
#: Logging: recipients of error emails
ADMINS = ['anu@hasgeek.com']
#: Log file
LOGFILE = 'error.log'
BENEFICIARY = 'HasGeek Media LLP'
EBS_ACCOUNT = ''
EBS_KEY = ''
