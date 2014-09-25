import os

from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import exceptions

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# TODO get token in session
MY_TOKEN = 'MIIOJwYJKoZIhvcNAQcCoIIOGDCCDhQCAQExCTAHBgUrDgMCGjCCDH0GCSqGSIb3DQEHAaCCDG4EggxqeyJhY2Nlc3MiOiB7InRva2VuIjogeyJpc3N1ZWRfYXQiOiAiMjAxNC0wOS0yNVQxMzo0NjozNC45MzEzNzEiLCAiZXhwaXJlcyI6ICIyMDE0LTA5LTI2VDEzOjQ2OjM0WiIsICJpZCI6ICJwbGFjZWhvbGRlciIsICJ0ZW5hbnQiOiB7ImRlc2NyaXB0aW9uIjogbnVsbCwgImVuYWJsZWQiOiB0cnVlLCAiaWQiOiAiODgyOWQ2MGMzZTU3NDkwODk3YjkzMDA2MTNlZmM2NDUiLCAibmFtZSI6ICJhZG1pbiJ9fSwgInNlcnZpY2VDYXRhbG9nIjogW3siZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4Nzc0L3YyLzg4MjlkNjBjM2U1NzQ5MDg5N2I5MzAwNjEzZWZjNjQ1IiwgInJlZ2lvbiI6ICJSZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4Nzc0L3YyLzg4MjlkNjBjM2U1NzQ5MDg5N2I5MzAwNjEzZWZjNjQ1IiwgImlkIjogIjNmZGZlNGFjNDdlZTRlM2NhMDQ3ZmZiODk5MWQ0NDE5IiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTAuMS4wLjQ2Ojg3NzQvdjIvODgyOWQ2MGMzZTU3NDkwODk3YjkzMDA2MTNlZmM2NDUifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiY29tcHV0ZSIsICJuYW1lIjogIm5vdmEifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTAuMS4wLjQ2Ojk2OTYvIiwgInJlZ2lvbiI6ICJSZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo5Njk2LyIsICJpZCI6ICIwZjEwM2NhYzY3ODE0NTU2YjMyYjg4ODY2ZGFhNGIzMyIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo5Njk2LyJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJuZXR3b3JrIiwgIm5hbWUiOiAibmV1dHJvbiJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6ODc3Ni92Mi84ODI5ZDYwYzNlNTc0OTA4OTdiOTMwMDYxM2VmYzY0NSIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6ODc3Ni92Mi84ODI5ZDYwYzNlNTc0OTA4OTdiOTMwMDYxM2VmYzY0NSIsICJpZCI6ICIyMjAwYmNiYmIxMTc0ZjZiODU4ZGQyZWRmOTBiM2M3YSIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4Nzc2L3YyLzg4MjlkNjBjM2U1NzQ5MDg5N2I5MzAwNjEzZWZjNjQ1In1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogInZvbHVtZXYyIiwgIm5hbWUiOiAiY2luZGVyIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4Nzc0L3YzIiwgInJlZ2lvbiI6ICJSZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4Nzc0L3YzIiwgImlkIjogIjJiMGM0YmQ1Zjg3MDRmOGQ5NTcyNzhlZTgzOTc3NjBkIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTAuMS4wLjQ2Ojg3NzQvdjMifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiY29tcHV0ZXYzIiwgIm5hbWUiOiAibm92YSJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6MzMzMyIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6MzMzMyIsICJpZCI6ICI1NjdmNjUzNzk1MzM0ZDljODk4NDkwMTE1ODFkODlkYSIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzEwLjEuMC40NjozMzMzIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogInMzIiwgIm5hbWUiOiAiczMifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTAuMS4wLjQ2OjkyOTIiLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTAuMS4wLjQ2OjkyOTIiLCAiaWQiOiAiM2VmOGFiODVjNjY0NDg1ODhlOWJhNTViMjk4ODg2ZjgiLCAicHVibGljVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6OTI5MiJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJpbWFnZSIsICJuYW1lIjogImdsYW5jZSJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6ODc3Ni92MS84ODI5ZDYwYzNlNTc0OTA4OTdiOTMwMDYxM2VmYzY0NSIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6ODc3Ni92MS84ODI5ZDYwYzNlNTc0OTA4OTdiOTMwMDYxM2VmYzY0NSIsICJpZCI6ICIzYmU0MzQ2YTZiOTk0MWI0OTc3MzI4NjM4ZjI5ZTc4MSIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4Nzc2L3YxLzg4MjlkNjBjM2U1NzQ5MDg5N2I5MzAwNjEzZWZjNjQ1In1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogInZvbHVtZSIsICJuYW1lIjogImNpbmRlciJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6ODc3My9zZXJ2aWNlcy9BZG1pbiIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6ODc3My9zZXJ2aWNlcy9DbG91ZCIsICJpZCI6ICIxYjZkMGM3OWFhZDQ0MzEzOWFhODlmOGYwOTMyOTE0NyIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzEwLjEuMC40Njo4NzczL3NlcnZpY2VzL0Nsb3VkIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogImVjMiIsICJuYW1lIjogImVjMiJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6MzUzNTcvdjIuMCIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xMC4xLjAuNDY6NTAwMC92Mi4wIiwgImlkIjogIjJkYjFmZGU3MWZiYjQ1ZDZiYTBmY2QzOTg0ZGZmOGVkIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTAuMS4wLjQ2OjUwMDAvdjIuMCJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJpZGVudGl0eSIsICJuYW1lIjogImtleXN0b25lIn1dLCAidXNlciI6IHsidXNlcm5hbWUiOiAiYWRtaW4iLCAicm9sZXNfbGlua3MiOiBbXSwgImlkIjogIjE1OTMzZWUwYWEzNjRlMGE5NGE0OGNmZmExMmExYWEyIiwgInJvbGVzIjogW3sibmFtZSI6ICJhZG1pbiJ9XSwgIm5hbWUiOiAiYWRtaW4ifSwgIm1ldGFkYXRhIjogeyJpc19hZG1pbiI6IDAsICJyb2xlcyI6IFsiYWM1MzJkYzE3Zjk3NDNkNjg3ZmJmZWE2MTAwZTc4YWEiXX19fTGCAYEwggF9AgEBMFwwVzELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVVuc2V0MQ4wDAYDVQQHDAVVbnNldDEOMAwGA1UECgwFVW5zZXQxGDAWBgNVBAMMD3d3dy5leGFtcGxlLmNvbQIBATAHBgUrDgMCGjANBgkqhkiG9w0BAQEFAASCAQCJ3o2A-abXrNIWXHtxgfursBb-r9qECBaKEQ1SLWJT8ZcdCq4Q-pMcGrVqH8Hy-qrlC-aMndFPD25Iu2sLMB11g4TRm6ywi3iDL7kloU9bV2cveT1LhXwUflXEkY+Pc47Yi3R53Bim7mYtOiebI7sXvS3OHS1px+R+6ljPu0ThzNBtbkBPqBRjQZJ7Df8moZRYfZgHmFGbd-HDGPDgfQVj-Pg3bz+oRAXUxqlZEbdBp2XcjcEhMI4CDsqjASWt6gVkZ6YVd7ONK0GtR-EAq1-xOZLCdoL1O5iwLpJ11NrFdU4DhlQBbsU-4R3VIr2m1NkUOWF9OgNdv1DGGphFwxJQ'
MY_ENDPOINT = 'http://150.165.15.107:8182'

# Required for Django 1.5.
# If horizon is running in production (DEBUG is False), set this
# with the list of host/domain names that the application can serve.
# For more information see:
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
#ALLOWED_HOSTS = ['horizon.example.com', ]

# Set SSL proxy settings:
# For Django 1.4+ pass this header from the proxy after terminating the SSL,
# and don't forget to strip it from the client's request.
# For more information see:
# https://docs.djangoproject.com/en/1.4/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# If Horizon is being served through SSL, then uncomment the following two
# settings to better secure the cookies from security exploits
#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True

# Overrides for OpenStack API versions. Use this setting to force the
# OpenStack dashboard to use a specfic API version for a given service API.
# NOTE: The version should be formatted as it appears in the URL for the
# service API. For example, The identity service APIs have inconsistent
# use of the decimal point, so valid options would be "2.0" or "3".
# OPENSTACK_API_VERSIONS = {
#     "identity": 3
# }

# Set this to True if running on multi-domain model. When this is enabled, it
# will require user to enter the Domain name in addition to username for login.
# OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = False

# Overrides the default domain used when running on single-domain model
# with Keystone V3. All entities will be created in the default domain.
# OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

# Set Console type:
# valid options would be "AUTO", "VNC" or "SPICE"
# CONSOLE_TYPE = "AUTO"

# Default OpenStack Dashboard configuration.
HORIZON_CONFIG = {
#     'dashboards': ('project', 'admin', 'settings',),
    'dashboards': ('settings', 'fogbow'),
    'default_dashboard': 'fogbow',
    'user_home': 'openstack_dashboard.views.get_user_home',
    'ajax_queue_limit': 10,
    'auto_fade_alerts': {
        'delay': 3000,
        'fade_duration': 1500,
        'types': ['alert-success', 'alert-info']
    },
    'help_url': "http://www.fogbowcloud.org/",
    'exceptions': {'recoverable': exceptions.RECOVERABLE,
                   'not_found': exceptions.NOT_FOUND,
                   'unauthorized': exceptions.UNAUTHORIZED},
}

# Specify a regular expression to validate user passwords.
# HORIZON_CONFIG["password_validator"] = {
#     "regex": '.*',
#     "help_text": _("Your password does not meet the requirements.")
# }

# Disable simplified floating IP address management for deployments with
# multiple floating IP pools or complex network requirements.
# HORIZON_CONFIG["simple_ip_management"] = False

# Turn off browser autocompletion for the login form if so desired.
# HORIZON_CONFIG["password_autocomplete"] = "off"

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

# Set custom secret key:
# You can either set it to a specific value or you can let horizion generate a
# default secret key that is unique on this machine, e.i. regardless of the
# amount of Python WSGI workers (if used behind Apache+mod_wsgi): However, there
# may be situations where you would want to set this explicitly, e.g. when
# multiple dashboard instances are distributed on different machines (usually
# behind a load-balancer). Either you have to make sure that a session gets all
# requests routed to the same dashboard instance or you set the same SECRET_KEY
# for all of them.
from horizon.utils import secret_key
SECRET_KEY = secret_key.generate_or_read_from_file(os.path.join(LOCAL_PATH, '.secret_key_store'))

# We recommend you use memcached for development; otherwise after every reload
# of the django development server, you will have to login again. To use
# memcached set CACHES to something like
# CACHES = {
#    'default': {
#        'BACKEND' : 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION' : '127.0.0.1:11211',
#    }
#}

CACHES = {
    'default': {
        'BACKEND' : 'django.core.cache.backends.locmem.LocMemCache'
    }
}

# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or send them to /dev/null
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Configure these for your outgoing email host
# EMAIL_HOST = 'smtp.my-company.com'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'djangomail'
# EMAIL_HOST_PASSWORD = 'top-secret!'

# For multiple regions uncomment this configuration, and add (endpoint, title).
# AVAILABLE_REGIONS = [
#     ('http://cluster1.example.com:5000/v2.0', 'cluster1'),
#     ('http://cluster2.example.com:5000/v2.0', 'cluster2'),
# ]

OPENSTACK_HOST = "150.165.15.107"
OPENSTACK_KEYSTONE_URL = "http://%s:5000/v2.0" % OPENSTACK_HOST
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "admin"

# Disable SSL certificate checks (useful for self-signed certificates):
# OPENSTACK_SSL_NO_VERIFY = True

# The CA certificate to use to verify SSL connections
# OPENSTACK_SSL_CACERT = '/path/to/cacert.pem'

# The OPENSTACK_KEYSTONE_BACKEND settings can be used to identify the
# capabilities of the auth backend for Keystone.
# If Keystone has been configured to use LDAP as the auth backend then set
# can_edit_user to False and name to 'ldap'.
#
# TODO(tres): Remove these once Keystone has an API to identify auth backend.
OPENSTACK_KEYSTONE_BACKEND = {
    'name': 'native',
    'can_edit_user': True,
    'can_edit_group': True,
    'can_edit_project': True,
    'can_edit_domain': True,
    'can_edit_role': True
}

OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': True,
}

# The OPENSTACK_NEUTRON_NETWORK settings can be used to enable optional
# services provided by neutron. Options currenly available are load
# balancer service, security groups, quotas, VPN service.
OPENSTACK_NEUTRON_NETWORK = {
    'enable_lb': False,
    'enable_firewall': False,
    'enable_quotas': True,
    'enable_vpn': False,
    # The profile_support option is used to detect if an external router can be
    # configured via the dashboard. When using specific plugins the
    # profile_support can be turned on if needed.
    'profile_support': None,
    #'profile_support': 'cisco',
}

# The OPENSTACK_IMAGE_BACKEND settings can be used to customize features
# in the OpenStack Dashboard related to the Image service, such as the list
# of supported image formats.
# OPENSTACK_IMAGE_BACKEND = {
#     'image_formats': [
#         ('', ''),
#         ('aki', _('AKI - Amazon Kernel Image')),
#         ('ami', _('AMI - Amazon Machine Image')),
#         ('ari', _('ARI - Amazon Ramdisk Image')),
#         ('iso', _('ISO - Optical Disk Image')),
#         ('qcow2', _('QCOW2 - QEMU Emulator')),
#         ('raw', _('Raw')),
#         ('vdi', _('VDI')),
#         ('vhd', _('VHD')),
#         ('vmdk', _('VMDK'))
#     ]
# }

# OPENSTACK_ENDPOINT_TYPE specifies the endpoint type to use for the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is 'publicURL'.
#OPENSTACK_ENDPOINT_TYPE = "publicURL"

# SECONDARY_ENDPOINT_TYPE specifies the fallback endpoint type to use in the
# case that OPENSTACK_ENDPOINT_TYPE is not present in the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is None.  This
# value should differ from OPENSTACK_ENDPOINT_TYPE if used.
#SECONDARY_ENDPOINT_TYPE = "publicURL"

# The number of objects (Swift containers/objects or images) to display
# on a single page before providing a paging element (a "more" link)
# to paginate results.
API_RESULT_LIMIT = 1000
API_RESULT_PAGE_SIZE = 20

# The timezone of the server. This should correspond with the timezone
# of your entire OpenStack installation, and hopefully be in UTC.
TIME_ZONE = "UTC"

# When launching an instance, the menu of available flavors is
# sorted by RAM usage, ascending.  Provide a callback method here
# (and/or a flag for reverse sort) for the sorted() method if you'd
# like a different behaviour.  For more info, see
# http://docs.python.org/2/library/functions.html#sorted
# CREATE_INSTANCE_FLAVOR_SORT = {
#     'key': my_awesome_callback_method,
#     'reverse': False,
# }

# The Horizon Policy Enforcement engine uses these values to load per service
# policy rule files. The content of these files should match the files the
# OpenStack services are using to determine role based access control in the
# target installation.

# Path to directory containing policy.json files
#POLICY_FILES_PATH = os.path.join(ROOT_PATH, "conf")
# Map of local copy of service policy files
#POLICY_FILES = {
#    'identity': 'keystone_policy.json',
#    'compute': 'nova_policy.json'
#}

# Trove user and database extension support. By default support for
# creating users and databases on database instances is turned on.
# To disable these extensions set the permission here to something
# unusable such as ["!"].
# TROVE_ADD_USER_PERMS = []
# TROVE_ADD_DATABASE_PERMS = []

LOGGING = {
    'version': 1,
    # When set to True this will disable all logging except
    # for loggers specified in this configuration dictionary. Note that
    # if nothing is specified here and disable_existing_loggers is True,
    # django.db.backends will still log unless it is disabled explicitly.
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'INFO',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            # Set the level to "DEBUG" for verbose output logging.
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # Logging from django.db.backends is VERY verbose, send to null
        # by default.
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
        },
        'requests': {
            'handlers': ['null'],
            'propagate': False,
        },
        'horizon': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'openstack_dashboard': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'novaclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cinderclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'keystoneclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'glanceclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'neutronclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'heatclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ceilometerclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'troveclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'swiftclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'openstack_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'nose.plugins.manager': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'iso8601': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

SECURITY_GROUP_RULES = {
    'all_tcp': {
        'name': 'ALL TCP',
        'ip_protocol': 'tcp',
        'from_port': '1',
        'to_port': '65535',
    },
    'all_udp': {
        'name': 'ALL UDP',
        'ip_protocol': 'udp',
        'from_port': '1',
        'to_port': '65535',
    },
    'all_icmp': {
        'name': 'ALL ICMP',
        'ip_protocol': 'icmp',
        'from_port': '-1',
        'to_port': '-1',
    },
    'ssh': {
        'name': 'SSH',
        'ip_protocol': 'tcp',
        'from_port': '22',
        'to_port': '22',
    },
    'smtp': {
        'name': 'SMTP',
        'ip_protocol': 'tcp',
        'from_port': '25',
        'to_port': '25',
    },
    'dns': {
        'name': 'DNS',
        'ip_protocol': 'tcp',
        'from_port': '53',
        'to_port': '53',
    },
    'http': {
        'name': 'HTTP',
        'ip_protocol': 'tcp',
        'from_port': '80',
        'to_port': '80',
    },
    'pop3': {
        'name': 'POP3',
        'ip_protocol': 'tcp',
        'from_port': '110',
        'to_port': '110',
    },
    'imap': {
        'name': 'IMAP',
        'ip_protocol': 'tcp',
        'from_port': '143',
        'to_port': '143',
    },
    'ldap': {
        'name': 'LDAP',
        'ip_protocol': 'tcp',
        'from_port': '389',
        'to_port': '389',
    },
    'https': {
        'name': 'HTTPS',
        'ip_protocol': 'tcp',
        'from_port': '443',
        'to_port': '443',
    },
    'smtps': {
        'name': 'SMTPS',
        'ip_protocol': 'tcp',
        'from_port': '465',
        'to_port': '465',
    },
    'imaps': {
        'name': 'IMAPS',
        'ip_protocol': 'tcp',
        'from_port': '993',
        'to_port': '993',
    },
    'pop3s': {
        'name': 'POP3S',
        'ip_protocol': 'tcp',
        'from_port': '995',
        'to_port': '995',
    },
    'ms_sql': {
        'name': 'MS SQL',
        'ip_protocol': 'tcp',
        'from_port': '1433',
        'to_port': '1433',
    },
    'mysql': {
        'name': 'MYSQL',
        'ip_protocol': 'tcp',
        'from_port': '3306',
        'to_port': '3306',
    },
    'rdp': {
        'name': 'RDP',
        'ip_protocol': 'tcp',
        'from_port': '3389',
        'to_port': '3389',
    },
}
