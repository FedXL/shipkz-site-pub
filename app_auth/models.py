import uuid
from django.contrib.auth.models import  AbstractUser
from django.db import models
from legacy.models import Users , WebUsers

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False,null=True)
    repair_verification_token = models.TextField(editable=False,null=True, blank=True)

    def __str__(self):
        return self.username

    def to_dict(self):
        result ={
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser
        }
        return result

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True, related_name='profile')
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255,blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=100,blank=True, null=True)
    last_name = models.CharField(max_length=100,blank=True, null=True)
    patronymic_name = models.CharField(max_length=100,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cdek_address = models.CharField(max_length=255, blank=True, null=True)
    telegram_user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True, related_name='profile')
    web_user = models.ForeignKey(WebUsers, on_delete=models.CASCADE, blank=True, null=True, related_name='profile')

    def __str__(self):
        return f"{self.user.username} Profile"

    def to_dict(self):
        result = {
            'user': self.user.id,
            'profile_id': self.id,
            'phone': self.phone,
            'address': self.address,
            'telegram_id': self.telegram_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'patronymic_name': self.patronymic_name,
            'email': self.email,
            'cdek_address': self.cdek_address
        }
        return result

