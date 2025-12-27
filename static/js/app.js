// API基础URL
const API_BASE = '/api/v1';

// 全局状态
let token = localStorage.getItem('token');
let currentPage = 'dashboard';
let questionnaireItems = []; // 问卷题目

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuthStatus();
});

// 检查认证状态
async function checkAuthStatus() {
    try {
        const res = await fetch(`${API_BASE}/auth/status`);
        const data = await res.json();
        
        if (data.setup_required) {
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('setup-form').style.display = 'block';
        } else if (token) {
            await verifyToken();
        }
    } catch (e) {
        console.error('检查状态失败:', e);
    }
}

// 验证Token
async function verifyToken() {
    try {
        const res = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            showMainContent();
        } else {
            token = null;
            localStorage.removeItem('token');
        }
    } catch (e) {
        token = null;
        localStorage.removeItem('token');
    }
}

// 设置管理员
async function setupAdmin() {
    const username = document.getElementById('setup-username').value;
    const password = document.getElementById('setup-password').value;
    const password2 = document.getElementById('setup-password2').value;
    
    if (!username || !password) {
        showToast('请填写用户名和密码', 'error');
        return;
    }
    if (password !== password2) {
        showToast('两次密码不一致', 'error');
        return;
    }
    if (password.length < 6) {
        showToast('密码至少6位', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/setup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (res.ok) {
            showToast('管理员创建成功，请登录', 'success');
            document.getElementById('setup-form').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
        } else {
            const data = await res.json();
            showToast(data.detail || '创建失败', 'error');
        }
    } catch (e) {
        showToast('创建失败', 'error');
    }
}

// 登录
async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showToast('请填写用户名和密码', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            const data = await res.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            showMainContent();
        } else {
            const data = await res.json();
            showToast(data.detail?.message || data.detail || '登录失败', 'error');
        }
    } catch (e) {
        showToast('登录失败', 'error');
    }
}

// 退出登录
function logout() {
    token = null;
    localStorage.removeItem('token');
    location.reload();
}

// 显示主内容
function showMainContent() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('navbar').style.display = 'flex';
    document.getElementById('main-content').style.display = 'block';
    loadDashboard();
    loadClassOptions();
}

// 页面切换
function showPage(page) {
    currentPage = page;
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(`page-${page}`).style.display = 'block';
    document.querySelectorAll('.navbar-menu a').forEach(a => a.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
    
    switch(page) {
        case 'dashboard': loadDashboard(); break;
        case 'organization': loadOrganization(); break;
        case 'members': loadMembers(); break;
        case 'tasks': loadTasks(); break;
        case 'settings': loadSettings(); break;
    }
}

// API请求封装
async function api(url, options = {}) {
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }
    const res = await fetch(`${API_BASE}${url}`, { ...options, headers });
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail?.message || data.detail || '请求失败');
    }
    return res.json();
}

// 加载仪表板
async function loadDashboard() {
    try {
        const colleges = await api('/colleges/');
        const tasks = await api('/tasks/?limit=5');
        
        let totalMembers = 0;
        for (const college of colleges) {
            const grades = await api(`/grades/?college_id=${college.id}`);
            for (const grade of grades) {
                const classes = await api(`/classes/?grade_id=${grade.id}`);
                for (const cls of classes) {
                    const members = await api(`/members/?class_id=${cls.id}`);
                    totalMembers += members.length;
                }
            }
        }
        
        document.getElementById('dashboard-stats').innerHTML = `
            <div class="stat-card"><div class="stat-value">${colleges.length}</div><div class="stat-label">学院数</div></div>
            <div class="stat-card"><div class="stat-value">${totalMembers}</div><div class="stat-label">成员数</div></div>
            <div class="stat-card"><div class="stat-value">${tasks.length}</div><div class="stat-label">任务数</div></div>
        `;
        
        document.getElementById('recent-tasks').innerHTML = tasks.length ? 
            tasks.map(t => `<div style="padding:10px;border-bottom:1px solid #eee;">${t.title} - ${t.deadline ? new Date(t.deadline).toLocaleString() : '无截止时间'}</div>`).join('') :
            '<p style="color:#666;">暂无任务</p>';
    } catch (e) {
        console.error(e);
    }
}

// 加载班级选项
async function loadClassOptions() {
    try {
        const colleges = await api('/colleges/');
        let classOptions = '';
        
        for (const college of colleges) {
            const grades = await api(`/grades/?college_id=${college.id}`);
            for (const grade of grades) {
                const classes = await api(`/classes/?grade_id=${grade.id}`);
                for (const cls of classes) {
                    classOptions += `<option value="${cls.id}">${college.name} - ${grade.name} - ${cls.name}</option>`;
                }
            }
        }
        
        document.getElementById('member-class-filter').innerHTML = '<option value="">请选择班级</option>' + classOptions;
        document.getElementById('task-class-filter').innerHTML = '<option value="">全部班级</option>' + classOptions;
    } catch (e) {
        console.error(e);
    }
}

// 加载组织结构
async function loadOrganization() {
    try {
        const colleges = await api('/colleges/');
        let html = '<table class="table"><thead><tr><th>学院名称</th><th>年级数</th><th>操作</th></tr></thead><tbody>';
        
        for (const college of colleges) {
            const grades = await api(`/grades/?college_id=${college.id}`);
            html += `<tr>
                <td>${college.name}</td>
                <td>${grades.length}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="showGrades(${college.id}, '${college.name}')">查看年级</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteCollege(${college.id})">删除</button>
                </td>
            </tr>`;
        }
        
        html += '</tbody></table>';
        document.getElementById('college-list').innerHTML = colleges.length ? html : '<p style="color:#666;">暂无学院</p>';
    } catch (e) {
        showToast('加载失败', 'error');
    }
}

// 显示添加学院模态框
function showAddCollegeModal() {
    document.getElementById('modal-title').textContent = '添加学院';
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group">
            <label class="form-label">学院名称</label>
            <input type="text" id="college-name" class="form-control" placeholder="请输入学院名称">
        </div>
        <button class="btn btn-primary" onclick="addCollege()">添加</button>
    `;
    openModal();
}

async function addCollege() {
    const name = document.getElementById('college-name').value;
    if (!name) { showToast('请输入学院名称', 'error'); return; }
    try {
        await api('/colleges/', { method: 'POST', body: { name } });
        showToast('添加成功', 'success');
        closeModal();
        loadOrganization();
        loadClassOptions();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteCollege(id) {
    if (!confirm('确定删除该学院？将同时删除所有年级和班级！')) return;
    try {
        await fetch(`${API_BASE}/colleges/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        showToast('删除成功', 'success');
        loadOrganization();
        loadClassOptions();
    } catch (e) {
        showToast('删除失败', 'error');
    }
}


// 显示年级
async function showGrades(collegeId, collegeName) {
    const grades = await api(`/grades/?college_id=${collegeId}`);
    document.getElementById('modal-title').textContent = `${collegeName} - 年级管理`;
    
    let html = `<button class="btn btn-primary btn-sm" onclick="showAddGradeModal(${collegeId})" style="margin-bottom:15px;">+ 添加年级</button>`;
    html += '<table class="table"><thead><tr><th>年级名称</th><th>班级数</th><th>操作</th></tr></thead><tbody>';
    
    for (const grade of grades) {
        const classes = await api(`/classes/?grade_id=${grade.id}`);
        html += `<tr>
            <td>${grade.name}</td>
            <td>${classes.length}</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="showClasses(${grade.id}, '${grade.name}')">查看班级</button>
                <button class="btn btn-sm btn-danger" onclick="deleteGrade(${grade.id})">删除</button>
            </td>
        </tr>`;
    }
    
    html += '</tbody></table>';
    document.getElementById('modal-body').innerHTML = grades.length ? html : html + '<p style="color:#666;">暂无年级</p>';
    openModal();
}

function showAddGradeModal(collegeId) {
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group">
            <label class="form-label">年级名称</label>
            <input type="text" id="grade-name" class="form-control" placeholder="如：2024级">
        </div>
        <button class="btn btn-primary" onclick="addGrade(${collegeId})">添加</button>
    `;
}

async function addGrade(collegeId) {
    const name = document.getElementById('grade-name').value;
    if (!name) { showToast('请输入年级名称', 'error'); return; }
    try {
        await api('/grades/', { method: 'POST', body: { name, college_id: collegeId } });
        showToast('添加成功', 'success');
        closeModal();
        loadClassOptions();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteGrade(id) {
    if (!confirm('确定删除该年级？')) return;
    try {
        await fetch(`${API_BASE}/grades/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        showToast('删除成功', 'success');
        closeModal();
        loadClassOptions();
    } catch (e) {
        showToast('删除失败', 'error');
    }
}

// 显示班级
async function showClasses(gradeId, gradeName) {
    const classes = await api(`/classes/?grade_id=${gradeId}`);
    document.getElementById('modal-title').textContent = `${gradeName} - 班级管理`;
    
    let html = `<button class="btn btn-primary btn-sm" onclick="showAddClassModal(${gradeId})" style="margin-bottom:15px;">+ 添加班级</button>`;
    html += '<table class="table"><thead><tr><th>班级名称</th><th>操作</th></tr></thead><tbody>';
    
    for (const cls of classes) {
        html += `<tr><td>${cls.name}</td><td><button class="btn btn-sm btn-danger" onclick="deleteClass(${cls.id})">删除</button></td></tr>`;
    }
    
    html += '</tbody></table>';
    document.getElementById('modal-body').innerHTML = classes.length ? html : html + '<p style="color:#666;">暂无班级</p>';
    openModal();
}

function showAddClassModal(gradeId) {
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group">
            <label class="form-label">班级名称</label>
            <input type="text" id="class-name" class="form-control" placeholder="如：1班">
        </div>
        <button class="btn btn-primary" onclick="addClass(${gradeId})">添加</button>
    `;
}

async function addClass(gradeId) {
    const name = document.getElementById('class-name').value;
    if (!name) { showToast('请输入班级名称', 'error'); return; }
    try {
        await api('/classes/', { method: 'POST', body: { name, grade_id: gradeId } });
        showToast('添加成功', 'success');
        closeModal();
        loadClassOptions();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteClass(id) {
    if (!confirm('确定删除该班级？')) return;
    try {
        await fetch(`${API_BASE}/classes/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        showToast('删除成功', 'success');
        closeModal();
        loadClassOptions();
    } catch (e) {
        showToast('删除失败', 'error');
    }
}

// 成员管理
async function loadMembers() {
    const classId = document.getElementById('member-class-filter').value;
    if (!classId) {
        document.getElementById('member-list').innerHTML = '<p style="color:#666;">请先选择班级</p>';
        return;
    }
    
    try {
        const members = await api(`/members/?class_id=${classId}`);
        let html = '<table class="table"><thead><tr><th>学号</th><th>姓名</th><th>性别</th><th>寝室</th><th>QQ邮箱</th><th>操作</th></tr></thead><tbody>';
        
        for (const m of members) {
            html += `<tr>
                <td>${m.student_id}</td>
                <td>${m.name}</td>
                <td>${m.gender || '-'}</td>
                <td>${m.dormitory || '-'}</td>
                <td>${m.qq_email || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="editMember(${m.id})">编辑</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteMember(${m.id})">删除</button>
                </td>
            </tr>`;
        }
        
        html += '</tbody></table>';
        document.getElementById('member-list').innerHTML = members.length ? html : '<p style="color:#666;">暂无成员</p>';
    } catch (e) {
        showToast('加载失败', 'error');
    }
}

function downloadTemplate() {
    window.open(`${API_BASE}/members/template`, '_blank');
}

function showImportModal() {
    const classId = document.getElementById('member-class-filter').value;
    if (!classId) { showToast('请先选择班级', 'error'); return; }
    
    document.getElementById('modal-title').textContent = '导入成员';
    document.getElementById('modal-body').innerHTML = `
        <div class="upload-area" onclick="document.getElementById('import-file').click()">
            <div class="upload-icon">📁</div>
            <p>点击选择Excel文件</p>
        </div>
        <input type="file" id="import-file" accept=".xlsx,.xls" style="display:none;" onchange="importMembers(${classId})">
    `;
    openModal();
}

async function importMembers(classId) {
    const file = document.getElementById('import-file').files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(`${API_BASE}/members/import?class_id=${classId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        const data = await res.json();
        showToast(`导入完成：成功${data.success_count}，跳过${data.skip_count}，失败${data.error_count}`, 'success');
        closeModal();
        loadMembers();
    } catch (e) {
        showToast('导入失败', 'error');
    }
}

function showAddMemberModal() {
    const classId = document.getElementById('member-class-filter').value;
    if (!classId) { showToast('请先选择班级', 'error'); return; }
    
    document.getElementById('modal-title').textContent = '添加成员';
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group"><label class="form-label">学号*</label><input type="text" id="m-student-id" class="form-control"></div>
        <div class="form-group"><label class="form-label">姓名*</label><input type="text" id="m-name" class="form-control"></div>
        <div class="form-group"><label class="form-label">性别</label><select id="m-gender" class="form-control"><option value="">请选择</option><option value="男">男</option><option value="女">女</option></select></div>
        <div class="form-group"><label class="form-label">寝室号</label><input type="text" id="m-dormitory" class="form-control"></div>
        <div class="form-group"><label class="form-label">QQ邮箱</label><input type="text" id="m-email" class="form-control"></div>
        <button class="btn btn-primary" onclick="addMember(${classId})">添加</button>
    `;
    openModal();
}

async function addMember(classId) {
    const data = {
        student_id: document.getElementById('m-student-id').value,
        name: document.getElementById('m-name').value,
        gender: document.getElementById('m-gender').value || null,
        dormitory: document.getElementById('m-dormitory').value || null,
        qq_email: document.getElementById('m-email').value || null,
        class_id: classId
    };
    if (!data.student_id || !data.name) { showToast('请填写学号和姓名', 'error'); return; }
    try {
        await api('/members/', { method: 'POST', body: data });
        showToast('添加成功', 'success');
        closeModal();
        loadMembers();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteMember(id) {
    if (!confirm('确定删除该成员？')) return;
    try {
        await fetch(`${API_BASE}/members/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        showToast('删除成功', 'success');
        loadMembers();
    } catch (e) {
        showToast('删除失败', 'error');
    }
}


// 任务管理
async function loadTasks() {
    const classId = document.getElementById('task-class-filter').value;
    try {
        const url = classId ? `/tasks/?class_id=${classId}` : '/tasks/';
        const tasks = await api(url);
        
        let html = '';
        for (const t of tasks) {
            const stats = await api(`/tasks/${t.id}/stats`);
            const progress = stats.total_members > 0 ? (stats.submitted_count / stats.total_members * 100).toFixed(1) : 0;
            
            // 收集类型标签
            let typeLabels = '';
            const ct = t.collect_types || {};
            if (ct.file) typeLabels += '<span class="badge badge-secondary">📁 文件</span> ';
            if (ct.text) typeLabels += '<span class="badge badge-secondary">📝 文本</span> ';
            if (ct.image) typeLabels += '<span class="badge badge-secondary">🖼️ 图片</span> ';
            if (ct.questionnaire) typeLabels += '<span class="badge badge-secondary">📋 问卷</span> ';
            if (!typeLabels) typeLabels = '<span class="badge badge-secondary">📁 文件</span>';
            
            html += `<div class="card task-card" style="margin-bottom:15px;">
                <div class="card-header">
                    <h4>${t.title}</h4>
                    <div>
                        ${t.admin_only_visible ? '<span class="badge badge-info" title="仅管理员可见提交状态">🔒 私密</span>' : ''}
                        <span class="badge ${t.deadline && new Date(t.deadline) < new Date() ? 'badge-danger' : 'badge-success'}">
                            ${t.deadline ? new Date(t.deadline).toLocaleString() : '无截止时间'}
                        </span>
                    </div>
                </div>
                <div style="margin-bottom:10px;">${typeLabels}</div>
                <p style="color:#666;margin-bottom:15px;">${t.description || '无描述'}</p>
                <div class="stats-grid" style="margin-bottom:15px;">
                    <div class="stat-card"><div class="stat-value">${stats.submitted_count}</div><div class="stat-label">已提交</div></div>
                    <div class="stat-card"><div class="stat-value">${stats.not_submitted_count}</div><div class="stat-label">未提交</div></div>
                    <div class="stat-card"><div class="stat-value">${progress}%</div><div class="stat-label">完成率</div></div>
                </div>
                <div class="progress" style="margin-bottom:15px;"><div class="progress-bar" style="width:${progress}%"></div></div>
                <div class="task-actions">
                    <button class="btn btn-primary btn-sm" onclick="showTaskDetail(${t.id})">📋 查看详情</button>
                    <button class="btn btn-secondary btn-sm" onclick="copySubmitLink(${t.id})">🔗 复制链接</button>
                    <button class="btn btn-secondary btn-sm" onclick="exportTask(${t.id})">📥 导出文件</button>
                    <button class="btn btn-success btn-sm" onclick="sendReminder(${t.id})">📧 发送提醒</button>
                    <button class="btn btn-warning btn-sm" onclick="copyUnsubmittedList(${t.id})">📋 复制未交名单</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteTask(${t.id})">🗑️ 删除</button>
                </div>
            </div>`;
        }
        
        document.getElementById('task-list').innerHTML = tasks.length ? html : '<p style="color:#666;">暂无任务</p>';
    } catch (e) {
        showToast('加载失败', 'error');
    }
}

// 复制提交链接
function copySubmitLink(taskId) {
    const link = `${window.location.origin}/submit?task_id=${taskId}`;
    navigator.clipboard.writeText(link).then(() => {
        showToast('链接已复制', 'success');
    });
}

// 显示创建任务模态框
function showAddTaskModal() {
    questionnaireItems = [];
    document.getElementById('modal-title').textContent = '创建任务';
    
    const classOptions = document.getElementById('task-class-filter').innerHTML;
    
    document.getElementById('modal-body').innerHTML = `
        <div class="form-group"><label class="form-label">任务标题*</label><input type="text" id="t-title" class="form-control"></div>
        <div class="form-group"><label class="form-label">任务描述</label><textarea id="t-desc" class="form-control" rows="2"></textarea></div>
        <div class="form-group"><label class="form-label">所属班级*</label><select id="t-class" class="form-control">${classOptions}</select></div>
        <div class="form-group"><label class="form-label">截止时间</label><input type="datetime-local" id="t-deadline" class="form-control"></div>
        
        <div class="form-section">
            <h4 style="margin-bottom:15px;color:#333;">📦 收集类型（可多选）</h4>
            <div class="checkbox-group">
                <label class="checkbox-label"><input type="checkbox" id="ct-file" checked onchange="updateCollectTypeUI()"> 📁 文件</label>
                <label class="checkbox-label"><input type="checkbox" id="ct-image" onchange="updateCollectTypeUI()"> 🖼️ 图片</label>
                <label class="checkbox-label"><input type="checkbox" id="ct-text" onchange="updateCollectTypeUI()"> 📝 文本</label>
                <label class="checkbox-label"><input type="checkbox" id="ct-questionnaire" onchange="updateCollectTypeUI()"> 📋 问卷</label>
            </div>
        </div>
        
        <div id="file-options" class="form-section">
            <div class="form-group"><label class="form-label">允许的文件类型（留空不限制）</label>
            <input type="text" id="t-allowed-types" class="form-control" placeholder="如: .pdf,.doc,.docx,.zip"></div>
        </div>
        
        <div id="image-options" class="form-section" style="display:none;">
            <p style="color:#666;font-size:13px;">支持的图片格式: jpg, jpeg, png, gif, bmp, webp</p>
        </div>
        
        <div id="questionnaire-options" class="form-section" style="display:none;">
            <h4 style="margin-bottom:10px;">问卷题目设置</h4>
            <div id="questionnaire-items"></div>
            <button type="button" class="btn btn-secondary btn-sm" onclick="addQuestionnaireItem()">+ 添加题目</button>
        </div>
        
        <div class="form-group"><label class="form-label">每人需提交项数</label><input type="number" id="t-items" class="form-control" value="1" min="1"></div>
        <div class="form-group"><label class="form-label">每人最大上传次数</label><input type="number" id="t-max" class="form-control" value="1" min="1"></div>
        
        <div class="form-section">
            <h4 style="margin-bottom:15px;color:#333;">🔒 可见性设置</h4>
            <div class="form-group switch-group">
                <label class="switch"><input type="checkbox" id="t-admin-only"><span class="slider"></span></label>
                <span>仅管理员可见所有提交</span>
            </div>
            <div class="form-group switch-group">
                <label class="switch"><input type="checkbox" id="t-allow-user-visibility" checked><span class="slider"></span></label>
                <span>允许用户自选是否公开</span>
            </div>
        </div>
        
        <div class="form-group switch-group">
            <label class="switch"><input type="checkbox" id="t-modify" checked><span class="slider"></span></label>
            <span>允许修改已上传内容</span>
        </div>
        <div class="form-group switch-group">
            <label class="switch"><input type="checkbox" id="t-auto-remind"><span class="slider"></span></label>
            <span>启用自动提醒</span>
        </div>
        <div class="form-group"><label class="form-label">提前提醒时间（小时）</label><input type="number" id="t-remind-hours" class="form-control" value="24" min="1"></div>
        
        <button class="btn btn-primary" onclick="addTask()">创建任务</button>
    `;
    openModal();
}

// 更新收集类型UI
function updateCollectTypeUI() {
    document.getElementById('file-options').style.display = document.getElementById('ct-file').checked ? 'block' : 'none';
    document.getElementById('image-options').style.display = document.getElementById('ct-image').checked ? 'block' : 'none';
    document.getElementById('questionnaire-options').style.display = document.getElementById('ct-questionnaire').checked ? 'block' : 'none';
}

// 添加问卷题目
function addQuestionnaireItem() {
    const idx = questionnaireItems.length;
    questionnaireItems.push({ type: 'text', title: '', options: [], required: true });
    renderQuestionnaireItems();
}

// 渲染问卷题目
function renderQuestionnaireItems() {
    const container = document.getElementById('questionnaire-items');
    container.innerHTML = questionnaireItems.map((item, idx) => `
        <div class="questionnaire-item" style="border:1px solid #e0e0e0;padding:15px;margin-bottom:10px;border-radius:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <strong>题目 ${idx + 1}</strong>
                <button type="button" class="btn btn-sm btn-danger" onclick="removeQuestionnaireItem(${idx})">删除</button>
            </div>
            <div class="form-group">
                <label class="form-label">题目类型</label>
                <select class="form-control" onchange="updateQuestionnaireItem(${idx}, 'type', this.value)">
                    <option value="text" ${item.type === 'text' ? 'selected' : ''}>文本输入</option>
                    <option value="radio" ${item.type === 'radio' ? 'selected' : ''}>单选题</option>
                    <option value="checkbox" ${item.type === 'checkbox' ? 'selected' : ''}>多选题</option>
                    <option value="image" ${item.type === 'image' ? 'selected' : ''}>图片上传</option>
                    <option value="file" ${item.type === 'file' ? 'selected' : ''}>文件上传</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">题目标题</label>
                <input type="text" class="form-control" value="${item.title}" onchange="updateQuestionnaireItem(${idx}, 'title', this.value)">
            </div>
            ${['radio', 'checkbox'].includes(item.type) ? `
                <div class="form-group">
                    <label class="form-label">选项（每行一个）</label>
                    <textarea class="form-control" rows="3" onchange="updateQuestionnaireItem(${idx}, 'options', this.value)">${(item.options || []).join('\\n')}</textarea>
                </div>
            ` : ''}
            <div class="form-group switch-group">
                <label class="switch"><input type="checkbox" ${item.required ? 'checked' : ''} onchange="updateQuestionnaireItem(${idx}, 'required', this.checked)"><span class="slider"></span></label>
                <span>必填</span>
            </div>
        </div>
    `).join('');
}

// 更新问卷题目
function updateQuestionnaireItem(idx, field, value) {
    if (field === 'options') {
        questionnaireItems[idx].options = value.split('\n').filter(v => v.trim());
    } else {
        questionnaireItems[idx][field] = value;
    }
    if (field === 'type') {
        renderQuestionnaireItems();
    }
}

// 删除问卷题目
function removeQuestionnaireItem(idx) {
    questionnaireItems.splice(idx, 1);
    renderQuestionnaireItems();
}

async function addTask() {
    const classId = document.getElementById('t-class').value;
    if (!classId) { showToast('请选择班级', 'error'); return; }
    
    const collectTypes = {
        file: document.getElementById('ct-file').checked,
        image: document.getElementById('ct-image').checked,
        text: document.getElementById('ct-text').checked,
        questionnaire: document.getElementById('ct-questionnaire').checked
    };
    
    // 至少选择一种收集类型
    if (!collectTypes.file && !collectTypes.image && !collectTypes.text && !collectTypes.questionnaire) {
        showToast('请至少选择一种收集类型', 'error');
        return;
    }
    
    const allowedTypesStr = document.getElementById('t-allowed-types').value;
    const allowedTypes = allowedTypesStr ? allowedTypesStr.split(',').map(t => t.trim()).filter(t => t) : null;
    
    const data = {
        title: document.getElementById('t-title').value,
        description: document.getElementById('t-desc').value || null,
        class_id: parseInt(classId),
        collect_types: collectTypes,
        items_per_person: parseInt(document.getElementById('t-items').value) || 1,
        allowed_types: allowedTypes,
        questionnaire_config: collectTypes.questionnaire ? questionnaireItems : null,
        deadline: document.getElementById('t-deadline').value ? new Date(document.getElementById('t-deadline').value).toISOString() : null,
        max_uploads: parseInt(document.getElementById('t-max').value) || 1,
        allow_modify: document.getElementById('t-modify').checked,
        admin_only_visible: document.getElementById('t-admin-only').checked,
        allow_user_set_visibility: document.getElementById('t-allow-user-visibility').checked,
        auto_remind_enabled: document.getElementById('t-auto-remind').checked,
        remind_before_hours: parseInt(document.getElementById('t-remind-hours').value) || 24
    };
    
    if (!data.title) { showToast('请输入任务标题', 'error'); return; }
    
    try {
        await api('/tasks/', { method: 'POST', body: data });
        showToast('创建成功', 'success');
        closeModal();
        loadTasks();
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function deleteTask(id) {
    if (!confirm('确定删除该任务？')) return;
    try {
        await fetch(`${API_BASE}/tasks/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
        showToast('删除成功', 'success');
        loadTasks();
    } catch (e) {
        showToast('删除失败', 'error');
    }
}


// 查看任务详情
async function showTaskDetail(taskId) {
    try {
        const task = await api(`/tasks/${taskId}`);
        const members = await api(`/tasks/${taskId}/members`);
        const submissions = await api(`/submissions/?task_id=${taskId}`);
        const stats = task.stats || await api(`/tasks/${taskId}/stats`);
        
        document.getElementById('modal-title').textContent = task.title;
        
        const progress = stats.total_members > 0 ? (stats.submitted_count / stats.total_members * 100).toFixed(1) : 0;
        
        // 构建成员列表
        let memberHtml = '<div class="member-grid">';
        for (const m of members) {
            const submission = submissions.find(s => s.member_id === m.id);
            memberHtml += `<div class="member-card ${m.has_submitted ? 'submitted' : 'not-submitted'}" onclick="showMemberSubmission(${taskId}, ${m.id}, '${m.name}')">
                <div class="member-name">${m.name}</div>
                <div class="member-id">${m.student_id}</div>
                <div class="badge ${m.has_submitted ? 'badge-success' : 'badge-warning'}">${m.has_submitted ? '已提交' : '未提交'}</div>
                ${m.has_submitted && submission ? `<div class="submission-info">${getSubmissionSummary(submission)}</div>` : ''}
            </div>`;
        }
        memberHtml += '</div>';
        
        // 构建文件预览列表
        let filePreviewHtml = '';
        if (submissions.length > 0) {
            filePreviewHtml = '<div class="file-preview-list">';
            for (const s of submissions) {
                const member = members.find(m => m.id === s.member_id);
                filePreviewHtml += `
                    <div class="file-preview-card">
                        <div class="file-preview-icon">${getSubmissionIcon(s)}</div>
                        <div class="file-preview-info">
                            <div class="file-preview-name">${getSubmissionTitle(s)}</div>
                            <div class="file-preview-meta">
                                ${member?.name || '-'} (${member?.student_id || '-'}) · 
                                ${s.submission_type} · 
                                ${new Date(s.created_at).toLocaleString()}
                                ${s.is_private ? ' · 🔒私密' : ''}
                            </div>
                        </div>
                        <div class="file-preview-actions">
                            <button class="btn btn-sm btn-secondary" onclick="previewSubmission(${s.id})">👁️ 预览</button>
                            <button class="btn btn-sm btn-primary" onclick="downloadSubmission(${s.id})">📥 下载</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteSubmission(${s.id}, ${taskId})">🗑️</button>
                        </div>
                    </div>`;
            }
            filePreviewHtml += '</div>';
        } else {
            filePreviewHtml = '<p style="color:#999;text-align:center;padding:30px;">暂无提交</p>';
        }
        
        // 检查是否有文本或问卷提交
        const hasText = submissions.some(s => s.submission_type === 'text');
        const hasQuestionnaire = submissions.some(s => s.submission_type === 'questionnaire');
        
        // 构建标签页
        let tabsHtml = `
            <div class="tabs">
                <div class="tab active" onclick="switchTab('members-tab', this)">👥 成员状态</div>
                <div class="tab" onclick="switchTab('files-tab', this)">📁 提交预览 (${submissions.length})</div>
                ${hasText ? `<div class="tab" onclick="loadTextSummary(${task.id}, this)">📝 文本汇总</div>` : ''}
                ${hasQuestionnaire ? `<div class="tab" onclick="loadQuestionnaireSummary(${task.id}, this)">📋 问卷汇总</div>` : ''}
            </div>
        `;
        
        document.getElementById('modal-body').innerHTML = `
            <div class="task-detail-header">
                <p style="color:#666;margin-bottom:15px;">${task.description || '无描述'}</p>
                <div class="task-meta">
                    <span>📅 截止: ${task.deadline ? new Date(task.deadline).toLocaleString() : '无'}</span>
                    <span>📤 每人${task.items_per_person}项</span>
                    <span>${task.allow_modify ? '✅ 允许修改' : '❌ 不允许修改'}</span>
                    <span>${task.admin_only_visible ? '🔒 私密' : '👁️ 公开'}</span>
                </div>
            </div>
            
            <div class="task-detail-stats">
                <div class="task-detail-stat"><div class="value">${stats.submitted_count}</div><div class="label">已提交</div></div>
                <div class="task-detail-stat"><div class="value">${stats.not_submitted_count}</div><div class="label">未提交</div></div>
                <div class="task-detail-stat"><div class="value">${progress}%</div><div class="label">完成率</div></div>
            </div>
            
            ${tabsHtml}
            
            <div id="members-tab" class="tab-content active">${memberHtml}</div>
            <div id="files-tab" class="tab-content">${filePreviewHtml}</div>
            <div id="text-summary-tab" class="tab-content"></div>
            <div id="questionnaire-summary-tab" class="tab-content"></div>
        `;
        
        openModal();
    } catch (e) {
        showToast('加载失败', 'error');
    }
}

// 获取提交摘要
function getSubmissionSummary(s) {
    if (s.submission_type === 'text') return '📝 文本';
    if (s.submission_type === 'questionnaire') return '📋 问卷';
    if (s.submission_type === 'image') return '🖼️ ' + truncateFilename(s.original_filename || '图片', 10);
    return '📄 ' + truncateFilename(s.original_filename || '文件', 10);
}

// 获取提交图标
function getSubmissionIcon(s) {
    if (s.submission_type === 'text') return '📝';
    if (s.submission_type === 'questionnaire') return '📋';
    if (s.submission_type === 'image') return '🖼️';
    return getFileIcon(s.original_filename || '');
}

// 获取提交标题
function getSubmissionTitle(s) {
    if (s.submission_type === 'text') return '文本内容';
    if (s.submission_type === 'questionnaire') return '问卷答案';
    return s.original_filename || '文件';
}

// 切换标签页
function switchTab(tabId, tabEl) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tabEl.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

// 加载文本汇总
async function loadTextSummary(taskId, tabEl) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tabEl.classList.add('active');
    document.getElementById('text-summary-tab').classList.add('active');
    
    try {
        const data = await api(`/submissions/export/texts?task_id=${taskId}`);
        let html = `<div style="margin-bottom:15px;"><button class="btn btn-primary btn-sm" onclick="exportTextFile(${taskId})">📥 导出为TXT文件</button></div>`;
        
        if (data.texts.length === 0) {
            html += '<p style="color:#999;text-align:center;">暂无文本提交</p>';
        } else {
            html += '<div class="text-summary-list">';
            for (const t of data.texts) {
                html += `<div style="margin-bottom:15px;padding:15px;background:#f8f9fa;border-radius:8px;">
                    <div style="font-weight:600;color:#333;margin-bottom:8px;">👤 ${t.student_id} - ${t.member_name}</div>
                    <div style="color:#666;white-space:pre-wrap;word-wrap:break-word;">${escapeHtml(t.content)}</div>
                    <div style="font-size:12px;color:#999;margin-top:8px;">${t.created_at ? new Date(t.created_at).toLocaleString() : ''}</div>
                </div>`;
            }
            html += '</div>';
        }
        
        document.getElementById('text-summary-tab').innerHTML = html;
    } catch (e) {
        document.getElementById('text-summary-tab').innerHTML = '<p style="color:#dc3545;">加载失败</p>';
    }
}

// 加载问卷汇总
async function loadQuestionnaireSummary(taskId, tabEl) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tabEl.classList.add('active');
    document.getElementById('questionnaire-summary-tab').classList.add('active');
    
    try {
        const data = await api(`/submissions/export/questionnaires?task_id=${taskId}`);
        let html = `<div style="margin-bottom:15px;"><button class="btn btn-primary btn-sm" onclick="exportTask(${taskId})">📥 导出所有提交</button></div>`;
        
        if (data.questionnaires.length === 0) {
            html += '<p style="color:#999;text-align:center;">暂无问卷提交</p>';
        } else {
            html += '<div class="questionnaire-summary-list">';
            for (const q of data.questionnaires) {
                html += `<div style="margin-bottom:20px;padding:15px;background:#f8f9fa;border-radius:8px;">
                    <div style="font-weight:600;color:#333;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #e0e0e0;">👤 ${q.student_id} - ${q.member_name}</div>`;
                
                for (const ans of q.answers) {
                    html += `<div style="margin-bottom:10px;">
                        <div style="font-weight:500;color:#555;font-size:13px;">📋 ${escapeHtml(ans.question)}</div>
                        <div style="color:#333;padding-left:20px;">${escapeHtml(ans.answer || '(未填写)')}</div>
                    </div>`;
                }
                
                html += `<div style="font-size:12px;color:#999;margin-top:10px;">${q.created_at ? new Date(q.created_at).toLocaleString() : ''}</div>
                </div>`;
            }
            html += '</div>';
        }
        
        document.getElementById('questionnaire-summary-tab').innerHTML = html;
    } catch (e) {
        document.getElementById('questionnaire-summary-tab').innerHTML = '<p style="color:#dc3545;">加载失败</p>';
    }
}

// 导出文本文件
async function exportTextFile(taskId) {
    try {
        const res = await fetch(`${API_BASE}/submissions/export/text?task_id=${taskId}`, { method: 'POST' });
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const contentDisposition = res.headers.get('Content-Disposition');
            let filename = 'texts.txt';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename\*=UTF-8''(.+)/);
                if (match) filename = decodeURIComponent(match[1]);
            }
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('导出成功', 'success');
        } else {
            showToast('导出失败', 'error');
        }
    } catch (e) {
        showToast('导出失败', 'error');
    }
}

// 获取文件图标
function getFileIcon(filename) {
    const ext = (filename || '').split('.').pop().toLowerCase();
    const icons = {
        'pdf': '📕', 'doc': '📘', 'docx': '📘',
        'xls': '📗', 'xlsx': '📗', 'ppt': '📙', 'pptx': '📙',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️',
        'zip': '📦', 'rar': '📦', '7z': '📦',
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬',
        'mp3': '🎵', 'wav': '🎵', 'txt': '📄', 'md': '📄',
    };
    return icons[ext] || '📄';
}

// 截断文件名
function truncateFilename(filename, maxLen) {
    if (!filename || filename.length <= maxLen) return filename || '';
    const ext = filename.split('.').pop();
    const name = filename.slice(0, -(ext.length + 1));
    return name.slice(0, maxLen - ext.length - 4) + '...' + '.' + ext;
}

// 预览提交
async function previewSubmission(submissionId) {
    try {
        const res = await fetch(`${API_BASE}/submissions/${submissionId}/preview`);
        const data = await res.json();
        
        // 获取提交详情以获取task_id
        const subRes = await fetch(`${API_BASE}/submissions/${submissionId}`);
        const submission = await subRes.json();
        
        document.getElementById('modal-title').textContent = '预览';
        
        let content = '';
        if (data.type === 'text') {
            content = `<div class="preview-text"><pre style="white-space:pre-wrap;word-wrap:break-word;background:#f5f5f5;padding:15px;border-radius:8px;">${escapeHtml(data.content || '')}</pre></div>`;
        } else if (data.type === 'questionnaire') {
            // 获取任务配置以显示问题标题
            let taskConfig = [];
            try {
                const taskRes = await fetch(`${API_BASE}/tasks/${submission.task_id}`);
                const task = await taskRes.json();
                taskConfig = task.questionnaire_config || [];
            } catch (e) {}
            
            content = '<div class="preview-questionnaire" style="padding:10px;">';
            const answers = data.answers || {};
            for (const [key, value] of Object.entries(answers)) {
                const idx = parseInt(key);
                const questionTitle = taskConfig[idx]?.title || `问题 ${idx + 1}`;
                const displayValue = Array.isArray(value) ? value.join(', ') : (value || '(未填写)');
                content += `<div style="margin-bottom:15px;padding:12px;background:#f8f9fa;border-radius:8px;">
                    <div style="font-weight:600;color:#333;margin-bottom:6px;">📋 ${questionTitle}</div>
                    <div style="color:#666;">${escapeHtml(displayValue)}</div>
                </div>`;
            }
            content += '</div>';
        } else if (data.can_preview === false) {
            content = `<p style="text-align:center;color:#666;">该文件类型不支持预览，请下载查看</p>
                <p style="text-align:center;"><button class="btn btn-primary" onclick="downloadSubmission(${submissionId})">📥 下载文件</button></p>`;
        } else {
            // 图片预览
            content = `<div style="text-align:center;"><img src="${API_BASE}/submissions/${submissionId}/preview" style="max-width:100%;max-height:500px;border-radius:8px;"></div>`;
        }
        
        document.getElementById('modal-body').innerHTML = content;
        openModal();
    } catch (e) {
        showToast('预览失败', 'error');
    }
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 查看成员提交详情
async function showMemberSubmission(taskId, memberId, memberName) {
    try {
        const submissions = await api(`/submissions/?task_id=${taskId}&member_id=${memberId}`);
        
        document.getElementById('modal-title').textContent = `${memberName} - 提交详情`;
        
        let html = '';
        if (submissions.length > 0) {
            html = `<div class="submission-list">`;
            for (const s of submissions) {
                html += `<div class="submission-item">
                    <div class="submission-file">
                        <span class="file-icon">${getSubmissionIcon(s)}</span>
                        <div class="file-info">
                            <div class="file-name">${getSubmissionTitle(s)}</div>
                            <div class="file-meta">${s.submission_type} · ${new Date(s.created_at).toLocaleString()}${s.is_private ? ' · 🔒私密' : ''}</div>
                        </div>
                    </div>
                    <div class="submission-actions">
                        <button class="btn btn-sm btn-secondary" onclick="previewSubmission(${s.id})">预览</button>
                        <button class="btn btn-sm btn-primary" onclick="downloadSubmission(${s.id})">下载</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSubmission(${s.id}, ${taskId})">删除</button>
                    </div>
                </div>`;
            }
            html += '</div>';
        } else {
            html = '<p style="color:#666;text-align:center;padding:30px;">暂无提交记录</p>';
        }
        
        document.getElementById('modal-body').innerHTML = html;
        openModal();
    } catch (e) {
        showToast('加载失败', 'error');
    }
}

// 下载提交文件
function downloadSubmission(submissionId) {
    window.open(`${API_BASE}/submissions/${submissionId}/download`, '_blank');
}

// 删除提交
async function deleteSubmission(submissionId, taskId) {
    if (!confirm('确定删除该提交？')) return;
    try {
        await fetch(`${API_BASE}/submissions/${submissionId}`, { 
            method: 'DELETE', 
            headers: { 'Authorization': `Bearer ${token}` } 
        });
        showToast('删除成功', 'success');
        showTaskDetail(taskId);
    } catch (e) {
        showToast('删除失败', 'error');
    }
}

// 复制未提交名单
async function copyUnsubmittedList(taskId) {
    try {
        const data = await api(`/tasks/${taskId}/unsubmitted`);
        if (data.count === 0) {
            showToast('所有人都已提交！', 'success');
            return;
        }
        await navigator.clipboard.writeText(data.names_text);
        showToast(`已复制${data.count}人未交名单`, 'success');
    } catch (e) {
        showToast('复制失败', 'error');
    }
}

// 导出任务文件
async function exportTask(taskId) {
    try {
        const res = await fetch(`${API_BASE}/submissions/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId })
        });
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const contentDisposition = res.headers.get('Content-Disposition');
            let filename = 'submissions.zip';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename\*=UTF-8''(.+)/);
                if (match) filename = decodeURIComponent(match[1]);
            }
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('导出成功', 'success');
        } else {
            const data = await res.json();
            showToast(data.detail || '导出失败', 'error');
        }
    } catch (e) {
        showToast('导出失败: ' + e.message, 'error');
    }
}

// 发送提醒
async function sendReminder(taskId) {
    if (!confirm('确定向所有未提交成员发送提醒邮件？')) return;
    try {
        const data = await api(`/tasks/${taskId}/remind`, { method: 'POST', body: {} });
        showToast(`发送完成：成功${data.success}人，失败${data.failed}人`, data.success > 0 ? 'success' : 'error');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1024 / 1024).toFixed(1) + ' MB';
}


// 设置页面
async function loadSettings() {
    try {
        const naming = await api('/settings/naming-format');
        document.getElementById('naming-format').value = naming.format;
        
        const email = await api('/settings/email');
        document.getElementById('smtp-host').value = email.smtp_host;
        document.getElementById('smtp-port').value = email.smtp_port;
        document.getElementById('smtp-user').value = email.smtp_user;
    } catch (e) {
        console.error(e);
    }
}

async function saveNamingFormat() {
    const format = document.getElementById('naming-format').value;
    try {
        await api('/settings/naming-format', { method: 'PUT', body: { format } });
        showToast('保存成功', 'success');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

async function saveEmailConfig() {
    const data = {
        smtp_host: document.getElementById('smtp-host').value,
        smtp_port: parseInt(document.getElementById('smtp-port').value) || 465,
        smtp_user: document.getElementById('smtp-user').value,
        smtp_password: document.getElementById('smtp-password').value,
        smtp_use_ssl: true
    };
    try {
        await api('/settings/email', { method: 'PUT', body: data });
        showToast('保存成功', 'success');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// 模态框
function openModal() {
    document.getElementById('modal').classList.add('active');
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

// 消息提示
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
