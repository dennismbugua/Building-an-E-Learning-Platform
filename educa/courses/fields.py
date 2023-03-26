from django.db import models
from django.core.exceptions import ObjectDoesNotExist


# Django comes with a complete collection of model fields that you can use to build your models. However, you can also create your own model fields to store custom data or alter the behavior of existing fields.

# You need a field that allows you to define an order for the objects. An easy way to specify an order for objects using existing Django fields is by adding a PositiveIntegerField to your models. Using integers, you can easily specify the order of the objects. You can create a custom order field that inherits from PositiveIntegerField and provides additional behavior.

# There are two relevant functionalities that you will build into your order field:

# 1 Automatically assign an order value when no specific order is provided: When saving a new object with no specific order, your field should automatically assign the number that comes after the last existing ordered object. If there are two objects with orders 1 and 2 respectively, when saving a third object, you should automatically assign order 3 to it if no specific order has been provided.
# 2 Order objects with respect to other fields: Course modules will be ordered with respect to the course they belong to and module contents with respect to the module they belong to.


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            # no current value
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # filter by objects with the same field values
                    # for the fields in "for_fields"
                    query = {field: getattr(model_instance, field)
                             for field in self.for_fields}
                    qs = qs.filter(**query)
                # get the order of the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)


# This is the custom OrderField. It inherits from the PositiveIntegerField field provided by Django. Your OrderField field takes an optional for_fields parameter, which allows you to indicate the fields used to order the data.

# Your field overrides the pre_save() method of the PositiveIntegerField field, which is executed before saving the field to the database. In this method, you perform the following actions:

# 1 You check whether a value already exists for this field in the model instance. You use self.attname, which is the attribute name given to the field in the model. If the attribute’s value is different from None, you calculate the order you should give it as follows:
    # 1 You build a QuerySet to retrieve all objects for the field’s model. You retrieve the model class the field belongs to by accessing self.model.
    # 2 If there are any field names in the for_fields attribute of the field, you filter the QuerySet by the current value of the model fields in for_fields. By doing so, you calculate the order with respect to the given fields.
    # 3 You retrieve the object with the highest order with last_item = qs.latest(self.attname) from the database. If no object is found, you assume this object is the first one and assign order 0 to it.
    # 4 If an object is found, you add 1 to the highest order found.
    # 5 You assign the calculated order to the field’s value in the model instance using setattr() and return it.
# 2 If the model instance has a value for the current field, you use it instead of calculating it.

# When you create custom model fields, make them generic. Avoid hardcoding data that depends on a specific model or field. Your field should work in any model.
