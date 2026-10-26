from fastapi import Depends
from datetime import datetime, timedelta

from cache.helpers import CacheHelper
from cache.dependencies import get_cache_helper


# TODO: this function should check the auth api to see if a token is blacklisted.
async def check_blacklist_status() -> bool:
    return True


# TODO make this function call the auth API to blacklist the token
async def insert_blacklisted_token() -> bool:
    return True