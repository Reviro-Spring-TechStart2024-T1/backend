from django.db import models
from django.utils import timezone


class BaseModelManager(models.Manager):
    def get_queryset(self):
        '''Returns only non-deleted objects'''
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    everything = models.Manager()  # Manager to access to all objects, including deleted
    objects = BaseModelManager()  # Default manager filters out deleted objects and returns non-deleted

    def soft_delete(self):
        '''
        Marks the instance as deleted and saves the deletion time.
        '''
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        '''
        Restores a previously soft-deleted instance.
        '''
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def delete(self, hard=False):
        '''
        Use `hard=True` for physical deletion from the database.
        '''
        if hard:
            super().delete()  # Actual database deletion
        else:
            self.soft_delete()

    class Meta:
        abstract = True
