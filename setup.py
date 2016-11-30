from distutils.core import setup
setup(
  name = 'revlo',
  packages = ['revlo'],
  version = '0.14.1',
  description = 'Revlo Python Client',
  author = 'Scott Nguyen',
  author_email = 'scott.q.nguyen@gmail.com',
  url = 'https://github.com/teamrevlo/revlo-python-client',
  download_url = 'https://github.com/teamrevlo/revlo-python-client/tarball/0.14.1',
  keywords = ['revlo-api', 'revlo', 'revloapi'],
  classifiers = [
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5'
  ],
  install_requires=['requests==2.9.1']
)
