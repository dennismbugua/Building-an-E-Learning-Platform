from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField


# The following example shows what the data structure of your course catalog will look like:

# Subject 1
#   Course 1
#     Module 1
#       Content 1 (image)
#       Content 2 (text)
#     Module 2
#       Content 3 (text)
#       Content 4 (file)
#       Content 5 (video)
#       ...


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User,
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


# You name the new field order and specify that the ordering is calculated with respect to the course by setting for_fields=['course']. This means that the order for a new module will be assigned by adding 1 to the last module of the same Course object.
class Module(models.Model):
    course = models.ForeignKey(Course,
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # need to follow a particular order. This time, you specify that the order is calculated with respect to the module field.
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


# You plan to add different types of content to the course modules, such as text, images, files, and videos. Polymorphism is the provision of a single interface to entities of different types. You need a versatile data model that allows you to store diverse content that is accessible through a single interface.

class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': (
                                         'text',
                                         'video',
                                         'image',
                                         'file')})
    # store the primary key of the related object.
    object_id = models.PositiveIntegerField()
    # related object combining the two previous fields.
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


# Django supports model inheritance. It works in a similar way to standard class inheritance in Python. Django offers the following three options to use model inheritance:

# 1 Abstract models: Useful when you want to put some common information into several models.
    # An abstract model is a base class in which you define the fields you want to include in all child models. Django doesn’t create any database tables for abstract models. A database table is created for each child model, including the fields inherited from the abstract class and the ones defined in the child model.
    # To mark a model as abstract, you need to include abstract=True in its Meta class. Django will recognize that it is an abstract model and will not create a database table for it. To create child models, you just need to subclass the abstract model.

# 2 Multi-table model inheritance: Applicable when each model in the hierarchy is considered a complete model by itself.
    # In multi-table inheritance, each model corresponds to a database table. Django creates a OneToOneField field for the relationship between the child model and its parent model. To use multi-table inheritance, you have to subclass an existing model. Django will create a database table for both the original model and the sub-model.
    # Django will include an automatically generated OneToOneField field in the Text model and create a database table for each model.

# 3 Proxy models: Useful when you need to change the behavior of a model, for example, by including additional methods, changing the default manager, or using different meta options.
    # A proxy model changes the behavior of a model. Both models operate on the database table of the original model. To create a proxy model, add proxy=True to the Meta class of the model.
    # This model provides a default ordering for QuerySets and an additional created_delta() method. Both models, Content and OrderedContent, operate on the same database table, and objects are accessible via the ORM through either model.


class ItemBase(models.Model):
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()


# You have defined four different Content models that inherit from the ItemBase abstract model. They are as follows:

# Text: To store text content
# File: To store files, such as PDFs
# Image: To store image files
# Video: To store videos; you use an URLField field to provide a video URL in order to embed it

# Each child model contains the fields defined in the ItemBase class in addition to its own fields. A database table will be created for the Text, File, Image, and Video models, respectively. There will be no database table associated with the ItemBase model since it is an abstract model.
