from django import template


register = template.Library()


@register.filter
def running_total(objects_by_user):
    """
    Get the running total of the hours (duration of each shift) by user grouping
    :param objects_by_user:
    :return:
    """
    return sum(d.duration for d in objects_by_user)