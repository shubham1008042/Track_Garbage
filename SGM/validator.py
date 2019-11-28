from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', _('Please enter valid payroll ID.'))
zip_validate = RegexValidator(r'^[0-9]*$', _('Please enter valid zip code.'))
ssn_validate = RegexValidator(r'^\s*\d{3}-\d{2}-\d{4}\s*$',
                              _('Only numeric characters are allowed in following pattern 111-22-3333.'))
city_validate = RegexValidator(r'^[a-zA-Z]+$', _('Please enter valid city name.'))
civil_status_validate = RegexValidator(r'^[a-zA-Z]*$', _('Please enter valid civil status.'))
first_name_validate = RegexValidator(r'^[a-zA-Z]*$', _('Please enter valid first name.'))
last_name_validate = RegexValidator(r'^[a-zA-Z]*$', _('Please enter valid last name.'))
address_validate = RegexValidator(r'^[A-Za-z0-9\.\-\s\,]*$', _('Please enter valid address.'))
company_validate = RegexValidator(r'^[A-Za-z0-9\.\-\s\,]*$', _('Please enter valid company name.'))
def no_future(value):
    """
    validation for joining date
    :param value:
    :return:
    """
    today = date.today()
    val = today - value
    join = val.days
    if int(join) < 180:
        raise ValidationError(_('Sorry! Looks like you haven\'t completed '
                                '6 months with this company. You cannot proceed with this application.'))
def birth_validate(value):
    today = date.today()
    val = today - value
    birth = val.days
    if birth < 6570:
        raise ValidationError(_('Your age should be more then 18 years.'))
def income_validate(value):
    """
    gross income validation
    :param value:
    :return:
    """
    if value < 0.0:
        raise ValidationError(_('Please enter a value greater than 0.'))
def other_income_validate(value):
    """
    other income validation
    :param value:
    :return:
    """
    if value < -1:
        raise ValidationError(_('Please enter a value greater than or equal to 0.'))
def address_duration_validator(value):
    """
    address validation
    :param value:
    :return:
    """
    if value < 0:
        raise ValidationError(_('Please enter a value grater then 0.'))
phone_validate = RegexValidator(r'^\s*\(\d{3}\) \d{3}-\d{4}\s*$',
                                _('Please enter valid phone number. Phone number is allowed in following '
                                  'pattern (635) 635-6666.'))