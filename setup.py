from distutils.core import setup

setup(
    name='consolescrape',
    version='1.0',
    py_modules=['consolescrape'],
    install_requires=[
        'lxml>=4.4.2',
        'requests>=2.18.4'
    ],

    # metadata
    author='Soma Zsják',
    author_email='zsjaks@gmail.com',
    description='Scrape a console webshop for Nintendo Switch game price changes.',
    license='MIT',
    keywords='none',
)
