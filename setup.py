from setuptools import setup, find_packages

setup(
    name='Rufus',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'playwright', 'sentence-transformers', 'asyncio', 'urllib'
    ],
    author='Shrishailya chavan',
    author_email='shrichavan19@gmail.com',
    description='A package for intelligent web scraping and data extraction based on user prompts.',
    keywords='web scraping, data extraction, AI',
    url='https://github.com/yourusername/Rufus'
)
