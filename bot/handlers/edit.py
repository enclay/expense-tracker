import logging 
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

async def edit_insertion_handle(update: Update, context: CallbackContext):
    pass

async def edit_deletion_handle(update: Update, context: CallbackContext):
    pass
