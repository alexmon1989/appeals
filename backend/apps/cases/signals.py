from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document
import shutil


@receiver(post_delete, sender=Document)
def delete_document_folder_hook(sender, instance, using, **kwargs):
    shutil.rmtree(instance.folder_path, ignore_errors=True)
