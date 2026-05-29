from django import template

register = template.Library()


@register.filter
def status_color(status):
    mapping = {
        'not_started': 'secondary',
        'in_progress': 'warning',
        'completed': 'success',
        'on_hold': 'info',
        'archived': 'dark',
        'pending': 'secondary',
        'skipped': 'light',
        'blocked': 'danger',
    }
    return mapping.get(status, 'secondary')


@register.filter
def priority_color(priority):
    mapping = {
        'low': 'info',
        'medium': 'primary',
        'high': 'warning',
        'urgent': 'danger',
    }
    return mapping.get(priority, 'primary')


@register.filter
def node_status_class(status):
    mapping = {
        'pending': '',
        'in_progress': 'in_progress',
        'completed': 'completed',
        'skipped': 'skipped',
    }
    return mapping.get(status, '')


@register.filter
def result_box_class(status):
    mapping = {
        'not_started': 'empty',
        'in_progress': '',
        'completed': '',
        'blocked': 'problem',
    }
    return mapping.get(status, '')


@register.filter
def action_type_class(action_type):
    mapping = {
        'create': 'type-create',
        'update': 'type-update',
        'complete': 'type-complete',
        'problem': 'type-problem',
    }
    return mapping.get(action_type, 'type-update')
