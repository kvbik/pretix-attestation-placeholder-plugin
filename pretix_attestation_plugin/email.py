from pretix.base.email import BaseMailTextPlaceholder
from django.utils.translation import gettext_lazy as _

from .generator.java_generator_wrapper import generate_link

from .models import (
    AttestationLink,
    BaseURL,
    KeyFile,
)

"""
We need to register two email placeholders under the same name,
the proper one is picked based on the different context.
"""


class AttestationPlaceholder(BaseMailTextPlaceholder):
    def render(self, context):
        event = context["event"]
        position = self.get_position()

        try:
            base_url = BaseURL.objects.get(event=event).base_url
        except BaseURL.DoesNotExist:
            attestation_text = _("Attestation URL error - missing BaseURL - please contact support")
            return attestation_text
        try:
            path_to_key = KeyFile.objects.get(event=event).upload.path
        except KeyFile.DoesNotExist:
            attestation_text = _("Attestation URL error - missing KeyFile - please contact support")
            return attestation_text

        if not AttestationLink.objects.filter(order_position=position).exists():
            try:
                link = generate_link(position, path_to_key)
            except ValueError:
                attestation_text = _("Attestation URL error - problem generating AttestationLink - please contact support")
                return attestation_text
            AttestationLink.objects.update_or_create(
                order_position=position,
                defaults={"magic_link": link},
            )

        try:
            link = AttestationLink.objects.get(order_position=position).magic_link
            attestation_text = "{base_url}{link}".format(base_url=base_url, link=link)
        except AttestationLink.DoesNotExist:
            attestation_text = _("Attestation URL error - missing AttestationLink - please contact support")

        return attestation_text

    def render_sample(self, event):
        return "http://localhost/?ticket=MIGZMAoCAQYCAgTRA…"


class OrderAttestationPlaceholder(AttestationPlaceholder):
    """
    This should be called only if one Order has a position without filled attendee_email
    if everything is all right, PositionAttestationPlaceholder is used

    src/pretix/plugins/sendmail/signals.py::
        'pretix.plugins.sendmail.order.email.sent': _('The order received a mass email.'), # Imported order without attendee_email
        'pretix.plugins.sendmail.order.email.sent.attendee': _('A ticket holder of this order received a mass email.'), # Placed order with a proper position
    """
    identifier = "attestation_link"
    required_context = ['event', 'order']

    def get_position(self, context):
        """
        we expect only one position per order in this case

        FIXME: do sanity checks and fail nicely in the render() method
        """
        order = context['order']
        position = order.positions.first()
        return position


class PositionAttestationPlaceholder(AttestationPlaceholder):
    identifier = "attestation_link"
    required_context = ['event', 'position']

    def get_position(self, context):
        return context["position"]

