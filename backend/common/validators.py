from django.core.validators import RegexValidator


kyrgyz_phone_validator = RegexValidator(
    regex=r"^\+996\d{9}$",
    message="Phone number must be in Kyrgyz format: +996123123123.",
)
