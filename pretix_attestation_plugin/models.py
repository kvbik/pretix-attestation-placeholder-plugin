from django.core.files.storage import FileSystemStorage
from django.db import (
    models,
)
from pretix.base.models import (
    Event,
    OrderPosition,
)

# FIXME: merge BaseURL and KeyFile to a single Setting model
# ideally store the key file in a DB and pass it not on FS to the generator

class BaseURL(models.Model):
    """
    Represents a base url used for generating a attestation link
    """
    base_url = models.CharField(max_length=4096)

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True
    )


class AttestationLink(models.Model):
    """
    Represents an attestation link generated from an alphawallet tool for each order position
    """
    magic_link = models.CharField(max_length=4096)

    order_position = models.OneToOneField(
        OrderPosition,
        on_delete=models.CASCADE,
        primary_key=True
    )


class KeyFile(models.Model):
    """
    Represents a key file uploaded by an user, that will be used to generate an attestation link
    """
    upload = models.FileField(upload_to='pretix_attestation_plugin/keyfiles/', storage=FileSystemStorage())

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True
    )
