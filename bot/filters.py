from telegram.ext import filters

class MessageFilters:
    RAW_TEXT = filters.TEXT & ~filters.COMMAND
    JSON = filters.Document.MimeType("application/json")
