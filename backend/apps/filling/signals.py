from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Claim
import shutil


@receiver(post_delete, sender=Claim)
def delete_document_folder_hook(sender, instance, using, **kwargs):
    for doc in instance.document_set.all():
        shutil.rmtree(doc.folder_path,)
