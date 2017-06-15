from setuptools import setup

setup(name='ask_amy',
      version='0.2.3',
      description='Python framework for Alexa Skill development',
      url='https://github.com/dphiggs01/ask_amy',
      author='Dan Higgins',
      author_email='daniel.higgins@yahoo.com',
      license='MIT',
      packages=['ask_amy', 'ask_amy.cli', 'ask_amy.core', 'ask_amy.database', 'ask_amy.utilities'],
      test_suite='ask_amy.tests',
      entry_points={
          'console_scripts': ['ask-amy-cli=ask_amy.cli.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)