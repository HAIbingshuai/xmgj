from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    """事项 - 顶层实体"""
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('on_hold', '暂停'),
        ('archived', '已归档'),
    ]
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]

    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField('优先级', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人', related_name='items')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '事项'
        verbose_name_plural = '事项'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def timeline_node_count(self):
        return self.nodes.count()

    def latest_node_date(self):
        latest = self.nodes.order_by('-node_date').first()
        return latest.node_date if latest else None


class TimelineNode(models.Model):
    """时间轴节点"""
    NODE_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('skipped', '已跳过'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='所属事项', related_name='nodes')
    sequence = models.PositiveIntegerField('序号')
    title = models.CharField('节点标题', max_length=200)
    summary = models.TextField('概要', blank=True)
    node_date = models.DateField('节点日期')
    status = models.CharField('状态', max_length=20, choices=NODE_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '时间轴节点'
        verbose_name_plural = '时间轴节点'
        ordering = ['item', 'node_date', 'sequence']
        unique_together = ['item', 'sequence']

    def __str__(self):
        return f"{self.item.title} - {self.title}"

    def step_count(self):
        return self.steps.count()

    def completed_step_count(self):
        return self.steps.filter(status='completed').count()

    def progress_percentage(self):
        total = self.step_count()
        if total == 0:
            return 0
        return int((self.completed_step_count() / total) * 100)


class NodeStep(models.Model):
    """节点步骤"""
    STEP_STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('blocked', '受阻'),
    ]

    node = models.ForeignKey(TimelineNode, on_delete=models.CASCADE, verbose_name='所属节点', related_name='steps')
    sequence = models.PositiveIntegerField('步骤序号')
    title = models.CharField('步骤标题', max_length=200, blank=True, default='')
    content = models.TextField('步骤内容')
    status = models.CharField('状态', max_length=20, choices=STEP_STATUS_CHOICES, default='not_started')
    note = models.TextField('结果记录', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '节点步骤'
        verbose_name_plural = '节点步骤'
        ordering = ['node', 'sequence']
        unique_together = ['node', 'sequence']

    def __str__(self):
        return f"步骤 {self.sequence}: {self.content[:50]}"

    def attachment_count(self):
        return self.files.filter(file_type='attachment').count()

    def image_count(self):
        return self.files.filter(file_type='image').count()


class NodeStepFile(models.Model):
    """步骤文件（附件/图片）"""
    FILE_TYPE_CHOICES = [
        ('attachment', '附件'),
        ('image', '图片'),
    ]

    step = models.ForeignKey(NodeStep, on_delete=models.CASCADE, verbose_name='所属步骤', related_name='files')
    file_type = models.CharField('文件类型', max_length=10, choices=FILE_TYPE_CHOICES)
    file = models.FileField('文件', upload_to='step_files/%Y/%m/')
    original_name = models.CharField('原始文件名', max_length=255)
    file_size = models.PositiveIntegerField('文件大小(字节)', default=0)
    created_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        verbose_name = '步骤文件'
        verbose_name_plural = '步骤文件'
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name

    def size_display(self):
        if self.file_size < 1024:
            return f"{self.file_size}B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f}KB"
        else:
            return f"{self.file_size / 1024 / 1024:.1f}MB"

    def extension(self):
        _, ext = self.original_name.rsplit('.', 1)
        return ext.lower() if ext else ''


class NodeAction(models.Model):
    """操作记录"""
    ACTION_TYPE_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('complete', '完成'),
        ('problem', '问题'),
    ]

    node = models.ForeignKey(TimelineNode, on_delete=models.CASCADE, verbose_name='所属节点', related_name='actions')
    content = models.TextField('操作内容')
    action_type = models.CharField('操作类型', max_length=20, choices=ACTION_TYPE_CHOICES, default='update')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '操作记录'
        verbose_name_plural = '操作记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
