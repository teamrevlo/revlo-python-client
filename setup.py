from setuptools import setup

version='0.15.4'

setup(
  name = 'revlo',
  packages = ['revlo'],
  version = version,
  description = 'Revlo Python Client',
  author = 'Scott Nguyen',
  author_email = 'scott.q.nguyen@gmail.com',
  url = 'https://github.com/teamrevlo/revlo-python-client',
  download_url = 'https://github.com/teamrevlo/revlo-python-client/tarball/{}'.format(version),
  keywords = ['revlo-api', 'revlo', 'revloapi'],
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
  ],
  license='MIT',
  install_requires=['requests']
)
