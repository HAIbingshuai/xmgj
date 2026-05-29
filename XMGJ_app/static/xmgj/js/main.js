// 项目管家 - 主脚本

document.addEventListener('DOMContentLoaded', function() {

    // ===== 步骤卡片展开/收拢 =====
    document.querySelectorAll('.step-header').forEach(function(header) {
        header.addEventListener('click', function() {
            this.closest('.step-card').classList.toggle('expanded');
        });
    });

    // ===== 步骤复选框 AJAX + 进度刷新 =====
    document.querySelectorAll('.step-checkbox').forEach(function(cb) {
        cb.addEventListener('change', function() {
            var url = this.dataset.url;
            if (!url) return;
            var status = this.checked ? 'completed' : 'not_started';
            var formData = new FormData();
            formData.append('status', status);
            formData.append('csrfmiddlewaretoken', getCsrfToken());

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    // 刷新右侧进度条
                    var progressBars = document.querySelectorAll('.right-panel .progress-bar');
                    progressBars.forEach(function(bar) {
                        bar.style.width = data.progress + '%';
                    });
                    var progressText = document.querySelector('.right-panel .mb-2 .d-flex strong');
                    if (progressText) {
                        progressText.textContent = data.completed + ' / ' + data.total;
                    }
                    // 刷新左栏对应节点的进度
                    var selectedNode = document.querySelector('.timeline-item.selected');
                    if (selectedNode) {
                        var progSpan = selectedNode.querySelector('.node-step-progress');
                        if (progSpan) {
                            progSpan.innerHTML = '<i class="bi bi-check2-square me-1"></i>' + data.completed + '/' + data.total;
                        }
                        var microBar = selectedNode.querySelector('.progress-micro .progress-bar');
                        if (microBar) {
                            microBar.style.width = data.progress + '%';
                        }
                    }
                }
            });
        });
    });

    // ===== 时间轴节点点击选中 =====
    document.querySelectorAll('.timeline-node-card').forEach(function(card) {
        card.addEventListener('click', function() {
            var item = this.closest('.timeline-item');
            document.querySelectorAll('.timeline-item.selected').forEach(function(s) {
                s.classList.remove('selected');
            });
            item.classList.add('selected');
        });
    });

    // ===== 步骤行内编辑 =====
    // 点击 [编辑]
    document.querySelectorAll('.btn-edit-step').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var card = this.closest('.step-card');
            card.querySelector('.step-view-mode').style.display = 'none';
            card.querySelector('.step-edit-mode').style.display = 'block';
            card.querySelector('.step-view-btns').style.display = 'none';
            card.querySelector('.step-edit-btns').style.display = 'block';
        });
    });
    // 点击 [取消]
    document.querySelectorAll('.btn-cancel-edit').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var card = this.closest('.step-card');
            card.querySelector('.step-view-mode').style.display = 'block';
            card.querySelector('.step-edit-mode').style.display = 'none';
            card.querySelector('.step-view-btns').style.display = 'block';
            card.querySelector('.step-edit-btns').style.display = 'none';
        });
    });
    // 点击 [保存]
    document.querySelectorAll('.btn-save-step').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var card = this.closest('.step-card');
            var url = this.dataset.url;
            var content = card.querySelector('.step-edit-content').value;
            var note = card.querySelector('.step-edit-note').value;
            if (!content.trim()) return;

            var formData = new FormData();
            formData.append('content', content);
            formData.append('note', note);
            formData.append('csrfmiddlewaretoken', getCsrfToken());

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    // 更新查看模式的内容
                    card.querySelector('.step-view-mode .step-desc').textContent = content;
                    card.querySelector('.step-title').textContent = content.length > 60 ? content.substring(0, 60) + '...' : content;
                    card.querySelector('.step-preview').textContent = content;
                    // 更新结果区
                    var resultBox = card.querySelector('.step-view-mode .result-box');
                    if (note.trim()) {
                        if (resultBox) {
                            resultBox.innerHTML = resultBox.innerHTML.replace(/(>)(.*?)(<\/)/, '$1' + note + '$3');
                        }
                    }
                    // 切回查看模式
                    card.querySelector('.step-view-mode').style.display = 'block';
                    card.querySelector('.step-edit-mode').style.display = 'none';
                    card.querySelector('.step-view-btns').style.display = 'block';
                    card.querySelector('.step-edit-btns').style.display = 'none';
                }
            });
        });
    });

    // ===== 删除确认弹窗 =====
    document.querySelectorAll('[data-confirm-delete]').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var msg = this.dataset.confirmMsg || '确定要删除吗？此操作不可恢复。';
            if (confirm(msg)) {
                var url = this.dataset.url || this.getAttribute('href');
                if (url) {
                    var form = document.createElement('form');
                    form.method = 'POST';
                    form.action = url;
                    var csrf = document.createElement('input');
                    csrf.type = 'hidden';
                    csrf.name = 'csrfmiddlewaretoken';
                    csrf.value = getCsrfToken();
                    form.appendChild(csrf);
                    document.body.appendChild(form);
                    form.submit();
                }
            }
        });
    });

    // ===== 自动消失提示 =====
    document.querySelectorAll('.alert-auto-dismiss').forEach(function(alert) {
        setTimeout(function() {
            try {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch(e) {}
        }, 4000);
    });

    // ===== AJAX 文件上传（多选，不刷新页面） =====
    document.addEventListener('change', function(e) {
        var fileInput = e.target.closest('.upload-drawer-body .file-input');
        if (!fileInput) return;
        var body = fileInput.closest('.upload-drawer-body');
        var files = fileInput.files;
        if (!files.length) return;
        var uploadUrl = body.dataset.uploadUrl;
        var progressBar = body.querySelector('.upload-progress');
        var progressFill = body.querySelector('.upload-progress-bar');
        var progressText = body.querySelector('.upload-percent');
        var progressName = body.querySelector('.upload-filename');

        var i = 0;
        function uploadNext() {
            if (i >= files.length) { progressBar.style.display = 'none'; location.reload(); return; }
            var file = files[i];
            progressBar.style.display = 'block';
            progressName.textContent = file.name;
            progressFill.style.width = '0%';
            progressText.textContent = '0%';

            var formData = new FormData();
            formData.append('file', file);
            formData.append('csrfmiddlewaretoken', getCsrfToken());

            var xhr = new XMLHttpRequest();
            xhr.open('POST', uploadUrl, true);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    var pct = Math.round(e.loaded / e.total * 100);
                    progressFill.style.width = pct + '%';
                    progressText.textContent = pct + '%';
                }
            };
            xhr.onload = function() { i++; uploadNext(); };
            xhr.onerror = function() { progressName.textContent = file.name + ' 失败'; i++; setTimeout(function() { uploadNext(); }, 500); };
            xhr.send(formData);
        }
        uploadNext();
        fileInput.value = '';
    });

});

// ===== 图片预览（全局函数，供 onclick 调用） =====
function previewImage(src, name) {
    var el = document.getElementById('previewImageEl');
    var nameEl = document.getElementById('previewImageName');
    if (el) el.src = src;
    if (nameEl) nameEl.textContent = name || '';
    var modal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    modal.show();
}

// ===== CSRF Token 工具 =====
function getCsrfToken() {
    var name = 'csrftoken';
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
