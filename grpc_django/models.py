from django.contrib.auth.models import AbstractUser


# Create your models here.
class ContextUser(AbstractUser):
    """
    Just an abstract model class to represent Auth user coming as context in GRPC requests
    """

    class Meta:
        abstract = True

    def __str__(self):
        return " ".format([self.first_name, self.last_name])
