import os

from django.core.files.base import ContentFile
from django.db.models import Count
from celery import shared_task
from time import sleep
from django.conf import settings
import requests
import asyncio
import aiohttp
import logging
import time
import json

from . import models
from .parsers import AsyncParser, async_main

logger = logging.getLogger(__name__)


@shared_task
def task_1():
    logger.info('Task1 start')
    sleep(10)
    logger.info('Task1 end')


@shared_task
def get_data_from_olx_v1():
    # logger.info('\nStart parsing!\n')
    # start_time = time.perf_counter()
    # asyncio.run(async_main())
    # end_time = time.perf_counter()
    # parse_time = end_time - start_time
    # logger.info(f'\nParsing time: {parse_time}\n')
    dir_name = settings.BASE_DIR / 'json_files'
    file_name = os.listdir(dir_name)[0]
    logger.info('\nOpening jsonfile\n')
    with open(f'{dir_name}/{file_name}', mode='r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    logger.info('\nGetting data\n')

    flats = models.Flat.objects.all()
    if flats:
        logger.info('\nDelete all previous data\n')
        flats.delete()
    logger.info('\nAdd new data to db\n')

    for key, page_data in data.items():
        logger.info(f'\nKey = {key}\n')
        object_list: list = list()
        for index, obj in enumerate(page_data):
            image_list: list = list()
            logger.info(f'\nNumber = {index + 1}\n')
            title = obj.get('title')
            price = obj.get('price')
            link = obj.get('link')
            flat = models.Flat(title=title, price=price, link=link)
            flat.save()
            for image in obj.get('images'):

                content = requests.get(image).content

                image_list.append(models.Image(
                    flat=flat,
                    image=ContentFile(content)
                ))
            models.Image.objects.bulk_create(image_list)
        models.Flat.objects.bulk_create(object_list)
    logger.info('\nFinished process!\n')


if __name__ == '__main__':
    pass
