from distutils.core import setup
setup(
  name = 'pysecurityspy',
  packages=['pysecurityspy'],
  version = '0.1.2',
  license='MIT',
  description = 'Python Wrapper for SecuritySpy API', 
  author = 'Bjarne Riis',
  author_email = 'bjarne@briis.com',
  url = 'https://github.com/briis/pysecurityspy',
  keywords = ['SecuritySpy', 'Surveillance', 'Python', 'Home-Assistant'],
  install_requires=[
          'asyncio',
          'aiohttp',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)