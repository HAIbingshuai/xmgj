from django.contrib import admin
from .models import Item, TimelineNode, NodeStep, NodeStepFile, NodeAction


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'creator', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title',)


@admin.register(TimelineNode)
class TimelineNodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'item', 'node_date', 'status', 'sequence')
    list_filter = ('status',)


@admin.register(NodeStep)
class NodeStepAdmin(admin.ModelAdmin):
    list_display = ('node', 'sequence', 'content', 'status')
    list_filter = ('status',)


@admin.register(NodeStepFile)
class NodeStepFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'file_type', 'step', 'file_size', 'created_at')
    list_filter = ('file_type',)


@admin.register(NodeAction)
class NodeActionAdmin(admin.ModelAdmin):
    list_display = ('node', 'action_type', 'operator', 'created_at')
    list_filter = ('action_type',)
