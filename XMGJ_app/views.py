from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Max
from .models import Item, TimelineNode, NodeStep, NodeStepFile, NodeAction
from .forms import ItemForm, NodeForm, StepForm


# ===== 仪表盘 =====
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'xmgj/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        items = Item.objects.filter(creator=user)
        context['total_items'] = items.count()
        context['active_items'] = items.filter(status__in=['not_started', 'in_progress']).count()
        context['completed_items'] = items.filter(status='completed').count()
        context['urgent_items'] = items.filter(priority='urgent', status__in=['not_started', 'in_progress']).count()
        context['recent_items'] = items.order_by('-updated_at')[:5]
        return context


# ===== 事项列表（分组） =====
class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'xmgj/item_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        qs = Item.objects.filter(creator=self.request.user)
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        search = self.request.GET.get('search')
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_filter_param(self):
        return {
            'status': self.request.GET.get('status', ''),
            'priority': self.request.GET.get('priority', ''),
            'search': self.request.GET.get('search', ''),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_items = Item.objects.filter(creator=user)
        active_filter = self.request.GET.get('status', '')

        # 按状态分组
        status_order = ['in_progress', 'not_started', 'completed', 'on_hold']
        status_labels = {
            'in_progress': '进行中', 'not_started': '未开始',
            'completed': '已完成', 'on_hold': '暂停',
        }
        status_icons = {
            'in_progress': 'hourglass-split', 'not_started': 'circle',
            'completed': 'check-all', 'on_hold': 'pause-circle',
        }

        groups = []
        counts = {}
        for s in status_order:
            items_in_status = [item for item in context['items'] if item.status == s]
            counts[s] = len(items_in_status)
            if not active_filter or active_filter == s:
                if items_in_status:
                    groups.append({
                        'status': s,
                        'label': status_labels.get(s, s),
                        'icon': status_icons.get(s, 'kanban'),
                        'items': items_in_status,
                    })

        context['groups'] = groups
        context['counts'] = counts
        context['total_visible'] = len(context['items'])
        return context


# ===== 事项详情（核心页面） =====
class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'xmgj/item_detail.html'
    context_object_name = 'item'

    def get_queryset(self):
        return Item.objects.filter(creator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object
        nodes = item.nodes.prefetch_related('steps__files', 'actions__operator').all()

        selected_node_id = self.request.GET.get('node')
        if selected_node_id:
            context['selected_node'] = get_object_or_404(TimelineNode, pk=selected_node_id, item=item)
        elif nodes:
            context['selected_node'] = nodes.first()

        context['timeline_nodes'] = nodes

        total_steps = sum(n.step_count() for n in nodes)
        completed_steps = sum(n.completed_step_count() for n in nodes)
        context['total_steps'] = total_steps
        context['completed_steps'] = completed_steps
        context['overall_progress'] = int((completed_steps / total_steps * 100)) if total_steps > 0 else 0
        return context


# ===== 事项创建 =====
class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'xmgj/item_form.html'
    form_class = ItemForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        resp = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': str(reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.pk})),
            })
        messages.success(self.request, '事项创建成功')
        return resp

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, err_list in form.errors.items():
                for err in err_list:
                    errors.append(str(err))
            return JsonResponse({'success': False, 'error': '；'.join(errors)}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.pk})


# ===== 事项编辑 =====
class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'xmgj/item_form.html'
    form_class = ItemForm

    def get_queryset(self):
        return Item.objects.filter(creator=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, '事项已更新')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.pk})


# ===== 事项删除 =====
class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'xmgj/item_confirm_delete.html'
    success_url = reverse_lazy('xmgj:item_list')

    def get_queryset(self):
        return Item.objects.filter(creator=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, '事项已删除')
        return super().delete(request, *args, **kwargs)


# ===== 节点创建（支持 AJAX 弹窗） =====
class NodeCreateView(LoginRequiredMixin, CreateView):
    model = TimelineNode
    template_name = 'xmgj/node_form.html'
    form_class = NodeForm

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(Item, pk=kwargs['item_id'], creator=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.item = self.item
        max_seq = TimelineNode.objects.filter(item=self.item).aggregate(Max('sequence'))
        form.instance.sequence = (max_seq['sequence__max'] or 0) + 1
        resp = super().form_valid(form)
        NodeAction.objects.create(
            node=self.object,
            content=f"创建节点: {self.object.title}",
            action_type='create',
            operator=self.request.user
        )
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': str(reverse_lazy('xmgj:item_detail', kwargs={'pk': self.item.pk})),
            })
        messages.success(self.request, '节点创建成功')
        return resp

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, err_list in form.errors.items():
                for err in err_list:
                    errors.append(f'{field}: {err}')
            return JsonResponse({'success': False, 'error': '；'.join(errors)}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.item.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item
        return context


# ===== 节点编辑 =====
class NodeUpdateView(LoginRequiredMixin, UpdateView):
    model = TimelineNode
    template_name = 'xmgj/node_form.html'
    form_class = NodeForm

    def get_queryset(self):
        return TimelineNode.objects.filter(item__creator=self.request.user)

    def form_valid(self, form):
        resp = super().form_valid(form)
        NodeAction.objects.create(
            node=self.object,
            content=f"更新节点: {self.object.title}",
            action_type='update',
            operator=self.request.user
        )
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': str(reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.item.pk})),
            })
        messages.success(self.request, '节点已更新')
        return resp

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, err_list in form.errors.items():
                for err in err_list:
                    errors.append(str(err))
            return JsonResponse({'success': False, 'error': '；'.join(errors)}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.item.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.object.item
        return context


# ===== 节点删除 =====
class NodeDeleteView(LoginRequiredMixin, DeleteView):
    model = TimelineNode
    template_name = 'xmgj/node_confirm_delete.html'

    def get_queryset(self):
        return TimelineNode.objects.filter(item__creator=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, '节点已删除')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.item.pk})


# ===== 节点详情（AJAX） =====
class NodeDetailView(LoginRequiredMixin, DetailView):
    model = TimelineNode
    template_name = 'xmgj/includes/node_detail_panel.html'
    context_object_name = 'node'

    def get_queryset(self):
        return TimelineNode.objects.filter(item__creator=self.request.user).prefetch_related(
            'steps__files', 'actions__operator'
        )


# ===== 步骤创建 =====
class StepCreateView(LoginRequiredMixin, CreateView):
    model = NodeStep
    template_name = 'xmgj/step_form.html'
    form_class = StepForm

    def dispatch(self, request, *args, **kwargs):
        self.node = get_object_or_404(TimelineNode, pk=kwargs['node_id'], item__creator=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.node = self.node
        max_seq = NodeStep.objects.filter(node=self.node).aggregate(Max('sequence'))
        form.instance.sequence = (max_seq['sequence__max'] or 0) + 1
        resp = super().form_valid(form)
        NodeAction.objects.create(
            node=self.node,
            content=f"添加步骤 {form.instance.sequence}: {form.instance.content[:50]}",
            action_type='create',
            operator=self.request.user
        )
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': str(reverse_lazy('xmgj:item_detail', kwargs={'pk': self.node.item.pk}) + f'?node={self.node.pk}'),
            })
        messages.success(self.request, '步骤添加成功')
        return resp

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, err_list in form.errors.items():
                for err in err_list:
                    errors.append(str(err))
            return JsonResponse({'success': False, 'error': '；'.join(errors)}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.node.item.pk}) + f'?node={self.node.pk}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['node'] = self.node
        return context


# ===== 步骤编辑 =====
class StepUpdateView(LoginRequiredMixin, UpdateView):
    model = NodeStep
    template_name = 'xmgj/step_form.html'
    form_class = StepForm

    def get_queryset(self):
        return NodeStep.objects.filter(node__item__creator=self.request.user)

    def form_valid(self, form):
        resp = super().form_valid(form)
        NodeAction.objects.create(
            node=self.object.node,
            content=f"更新步骤 {self.object.sequence}: {self.object.content[:50]}",
            action_type='update',
            operator=self.request.user
        )
        messages.success(self.request, '步骤已更新')
        return resp

    def get_success_url(self):
        return reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.node.item.pk}) + f'?node={self.object.node.pk}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['node'] = self.object.node
        return context


# ===== 步骤删除 =====
class StepDeleteView(LoginRequiredMixin, DeleteView):
    model = NodeStep
    template_name = 'xmgj/step_confirm_delete.html'

    def get_queryset(self):
        return NodeStep.objects.filter(node__item__creator=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        node_pk = self.object.node.pk
        item_pk = self.object.node.item.pk
        NodeAction.objects.create(
            node=self.object.node,
            content=f"删除步骤 {self.object.sequence}: {self.object.content[:50]}",
            action_type='update',
            operator=request.user
        )
        self.object.delete()
        messages.success(request, '步骤已删除')
        return redirect(reverse_lazy('xmgj:item_detail', kwargs={'pk': item_pk}) + f'?node={node_pk}')


# ===== 步骤 AJAX 行内保存 =====
class StepInlineSaveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        step = get_object_or_404(NodeStep, pk=kwargs['pk'], node__item__creator=request.user)
        content = request.POST.get('content', '').strip()
        note = request.POST.get('note', '').strip()
        if content:
            step.content = content
            step.note = note
            step.save()
            NodeAction.objects.create(
                node=step.node,
                content=f"行内编辑步骤 {step.sequence}",
                action_type='update',
                operator=request.user
            )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': '内容不能为空'})


# ===== 步骤状态更新（AJAX） =====
class StepStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        step = get_object_or_404(NodeStep, pk=kwargs['pk'], node__item__creator=request.user)
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in NodeStep.STEP_STATUS_CHOICES]
        if new_status in valid_statuses:
            step.status = new_status
            step.save()
            action_type = 'complete' if new_status == 'completed' else 'problem' if new_status == 'blocked' else 'update'
            NodeAction.objects.create(
                node=step.node,
                content=f"步骤 {step.sequence} 状态变更为: {step.get_status_display()}",
                action_type=action_type,
                operator=request.user
            )
            return JsonResponse({
                'success': True,
                'progress': step.node.progress_percentage(),
                'completed': step.node.completed_step_count(),
                'total': step.node.step_count(),
            })
        return JsonResponse({'success': False, 'error': '无效状态'})


# ===== 文件上传 =====
class FileUploadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        step = get_object_or_404(NodeStep, pk=kwargs['step_id'], node__item__creator=request.user)
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'success': False, 'error': '未选择文件'})

        # 根据 MIME 自动识别文件类型
        content_type = uploaded_file.content_type or ''
        if content_type.startswith('image/'):
            file_type = 'image'
        else:
            file_type = 'attachment'

        node_step_file = NodeStepFile.objects.create(
            step=step,
            file_type=file_type,
            file=uploaded_file,
            original_name=uploaded_file.name,
            file_size=uploaded_file.size,
        )
        NodeAction.objects.create(
            node=step.node,
            content=f"上传{'附件' if file_type == 'attachment' else '图片'}: {uploaded_file.name}",
            action_type='update',
            operator=request.user
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'file_id': node_step_file.pk,
                'file_name': uploaded_file.name,
                'file_size': node_step_file.size_display(),
                'file_url': node_step_file.file.url,
            })
        messages.success(request, f'文件 {uploaded_file.name} 上传成功')
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('xmgj:item_detail', kwargs={'pk': step.node.item.pk})))


# ===== 文件删除 =====
class FileDeleteView(LoginRequiredMixin, DeleteView):
    model = NodeStepFile

    def get_queryset(self):
        return NodeStepFile.objects.filter(step__node__item__creator=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.file.delete(save=False)
        NodeAction.objects.create(
            node=self.object.step.node,
            content=f"删除{'附件' if self.object.file_type == 'attachment' else '图片'}: {self.object.original_name}",
            action_type='update',
            operator=request.user
        )
        messages.success(request, f'{self.object.original_name} 已删除')
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('xmgj:item_detail', kwargs={'pk': self.object.step.node.item.pk})))


# ===== 认证 =====
class LoginView(AuthLoginView):
    template_name = 'xmgj/auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('xmgj:dashboard')


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('xmgj:login')


class RegisterView(CreateView):
    template_name = 'xmgj/auth/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('xmgj:login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, '注册成功，请登录')
        return super().form_valid(form)
