import uuid
import subprocess
from django.db import models
from django.contrib.auth.models import AbstractUser

from .auth.hashers import check_password, make_password

from imagekit.processors import ResizeToFit
from imagekit.models import ProcessedImageField


class User(AbstractUser):
    """Custom User"""

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)


def profile_directory_path(instance, picture):
    # picture will be uploaded to MEDIA_ROOT/<UUID>/profile/<picture>
    return subprocess.check_output(
        'echo {0}/profile/{1}'.format(instance.id, picture),
        shell=True).rstrip().decode()


class UserProfile(models.Model):
    """User Profile"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField('birthdate', null=True, blank=True)
    about = models.TextField(max_length=256, null=True, blank=True)
    picture = ProcessedImageField(upload_to=profile_directory_path,
                                  processors=[ResizeToFit(200, 200)],
                                  format='JPEG',
                                  options={'quality': 60},
                                  null=True, blank=True)
    country = models.CharField(max_length=64, null=True, blank=True)
    education_level = models.CharField(max_length=32, null=True, blank=True)
    graduation_date = models.DateField(blank=True, null=True)
    dismissed_date = models.DateField(blank=True, null=True)
    create_on = models.DateField(auto_now_add=True)

    is_verified = models.BooleanField('verified', default=False)
    is_flagged = models.BooleanField('flagged', default=False)

    is_student = models.BooleanField('student', default=True)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def __str__(self):
        return self.user.get_full_name() or self.user.username
