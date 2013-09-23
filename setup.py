import sys
from setuptools import setup, find_packages

kwargs = {
    # Packages
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    'include_package_data': True,

    # Dependencies
    'install_requires': [
        'django>=1.4,<1.6',
    ],

    'test_suite': 'test_suite',

    # Metadata
    'name': 'django-webhooks2',
    'version': __import__('webhooks').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Simple webhooks for Django',
    'license': 'BSD',
    'keywords': 'webhooks events callbacks',
    'url': 'https://github.com/cbmi/django-webhooks/',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
    ],
}

setup(**kwargs)
