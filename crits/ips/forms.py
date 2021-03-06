import re

from django import forms
from django.forms.util import ErrorList

from crits.campaigns.campaign import Campaign
from crits.core.forms import add_bucketlist_to_form, add_ticket_to_form
from crits.core.handlers import get_item_names, get_source_names
from crits.core.user_tools import get_user_organization
from crits.core.handlers import get_object_types
from crits.core import form_consts

ip_choices = [(c[0], c[0]) for c in get_object_types(active=False, query={'type':'Address', 'name':{'$in':['cidr', re.compile('^ipv')]}})]

class AddIPForm(forms.Form):
    """
    Django form for adding an IP to CRITs.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    ip = forms.CharField(required=True,
                         label=form_consts.IP.IP_ADDRESS,
                         widget=forms.TextInput(attrs={'class': 'togglewithip'}))
    ip_type = forms.ChoiceField(required=True, label=form_consts.IP.IP_TYPE)
    analyst = forms.CharField(required=True, widget=forms.TextInput(attrs={'readonly':'readonly', 'class':'bulkskip'}), label=form_consts.IP.ANALYST)
    campaign = forms.ChoiceField(widget=forms.Select, required=False, label=form_consts.IP.CAMPAIGN)
    confidence = forms.ChoiceField(required=False, label=form_consts.IP.CAMPAIGN_CONFIDENCE)
    source = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': 'bulknoinitial'}), label=form_consts.IP.SOURCE)
    source_method = forms.CharField(required=False, label=form_consts.IP.SOURCE_METHOD)
    source_reference = forms.CharField(widget=forms.TextInput(attrs={'size':'90'}), required=False, label=form_consts.IP.SOURCE_REFERENCE)
    add_indicator = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'bulkskip'}), required=False, label=form_consts.IP.ADD_INDICATOR)
    indicator_reference = forms.CharField(widget=forms.TextInput(attrs={'size':'90', 'class':'bulkskip'}), required=False, label=form_consts.IP.INDICATOR_REFERENCE)

    def __init__(self, username, choices, *args, **kwargs):
        super(AddIPForm, self).__init__(*args, **kwargs)

        if choices is None:
            self.fields['ip_type'].choices = ip_choices
        else:
            self.fields['ip_type'].choices = choices

        self.fields['campaign'].choices = [('', '')] + [
                (c.name, c.name) for c in get_item_names(Campaign, True)]
        self.fields['confidence'].choices = [('', ''),
                                             ('low', 'low'),
                                             ('medium', 'medium'),
                                             ('high', 'high')]
        self.fields['source'].choices = [(c.name, c.name) for c in get_source_names(True, True, username)]
        self.fields['source'].initial = get_user_organization(username)
        self.fields['analyst'].initial = username

        add_bucketlist_to_form(self)
        add_ticket_to_form(self)

    def clean(self):
        cleaned_data = super(AddIPForm, self).clean()
        campaign = cleaned_data.get('campaign')

        if campaign:
            confidence = cleaned_data.get('confidence')

            if not confidence or confidence == '':
                self._errors.setdefault('confidence', ErrorList())
                self._errors['confidence'].append(u'This field is required if campaign is specified.')

        return cleaned_data
