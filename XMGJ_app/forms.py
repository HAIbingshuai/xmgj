from django import forms
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm
from .models import Item, TimelineNode, NodeStep


class ItemForm(forms.ModelForm):
    """事项表单"""
    class Meta:
        model = Item
        fields = ['title', 'description', 'status', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '输入事项标题，例如：企业官网建设项目',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '简要描述事项的背景、目标和范围...',
                'rows': 3,
            }),
            'status': forms.Select(attrs={
                'class': 'form-select tom-select',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select tom-select',
            }),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 2:
            raise forms.ValidationError('标题至少2个字符')
        return title


class NodeForm(forms.ModelForm):
    """时间轴节点表单"""
    class Meta:
        model = TimelineNode
        fields = ['title', 'summary', 'node_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '输入节点标题，例如：UI 视觉设计',
                'autofocus': True,
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '描述这个节点的核心任务和目标...',
                'rows': 3,
            }),
            'node_date': forms.DateInput(attrs={
                'class': 'form-control flatpickr',
                'placeholder': '选择日期',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select tom-select',
            }),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 2:
            raise forms.ValidationError('标题至少2个字符')
        return title


class StepForm(forms.ModelForm):
    """步骤表单"""
    class Meta:
        model = NodeStep
        fields = ['title', 'content', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：首页UI设计稿',
                'autofocus': True,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control auto-resize',
                'placeholder': '详细描述这个步骤需要做什么...',
                'rows': 2,
            }),
            'status': forms.Select(attrs={
                'class': 'form-select tom-select',
            }),
        }
