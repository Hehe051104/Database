// 全局变量存储图表实例
let deviceStatusChart = null;
let reservationStatusChart = null;

// 主要JavaScript文件
document.addEventListener("DOMContentLoaded", function () {
  // 初始化页面
  loadPage('dashboard');

  // 导航菜单点击事件
  document.querySelectorAll(".nav-link[data-page]").forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // 移除所有活动状态
      document.querySelectorAll(".nav-link").forEach((item) => {
        item.classList.remove("active");
      });

      // 设置当前项为活动状态
      this.classList.add("active");

      // 获取页面名称
      const pageName = this.getAttribute("data-page");

      // 更新页面标题
      document.getElementById("page-title").textContent = this.textContent.trim();

      // 加载相应页面
      loadPage(pageName);
    });
  });

  // 退出登录按钮点击事件
  document.getElementById("logout-btn").addEventListener("click", function (e) {
    e.preventDefault();

    axios
      .get("/api/auth/logout")
      .then(function (response) {
        if (response.data.status === "success") {
          window.location.href = "/api/auth/login";
        }
      })
      .catch(function (error) {
        console.error("退出登录失败:", error);
        alert("退出登录失败，请稍后重试");
      });
  });
});

// 加载仪表盘页面
function loadDashboard() {
  // 获取DOM元素 (现在它们应该存在了，因为骨架已注入)
  const totalDevicesEl = document.getElementById("total-devices");
  const availableDevicesEl = document.getElementById("available-devices");
  const pendingMaintenancesEl = document.getElementById("pending-maintenances");
  const deviceChartContainer = document.getElementById("device-status-chart-container");
  const reservationChartContainer = document.getElementById("reservation-status-chart-container");

  // 在API调用前设置加载状态文本 (确保元素存在)
  if (totalDevicesEl) totalDevicesEl.textContent = '...';
  if (availableDevicesEl) availableDevicesEl.textContent = '...';
  if (pendingMaintenancesEl) pendingMaintenancesEl.textContent = '...';
  if (deviceChartContainer) deviceChartContainer.innerHTML = '<p class="text-center">加载设备状态...</p>';
  if (reservationChartContainer) reservationChartContainer.innerHTML = '<p class="text-center">加载预约状态...</p>';

  axios.get("/api/stats/dashboard")
    .then(function (response) {
      if (response.data.status === "success" && response.data.dashboard) {
        const dashboard = response.data.dashboard;

        let calculatedTotalDevices = 0;
        let calculatedAvailableDevices = 0;

        // 处理和显示设备状态
        if (dashboard.device_status && Array.isArray(dashboard.device_status)) {
          dashboard.device_status.forEach(item => {
            const count = Number(item.count) || 0;
            calculatedTotalDevices += count;
            if (item.status === "空闲") {
              calculatedAvailableDevices = count;
            }
          });
          if (totalDevicesEl) totalDevicesEl.textContent = calculatedTotalDevices;
          if (availableDevicesEl) availableDevicesEl.textContent = calculatedAvailableDevices;
          
          if (deviceChartContainer) {
            let deviceStatusHtml = '<div class="row text-center g-3">'; // Added g-3 for spacing
            dashboard.device_status.forEach(item => {
              let bgColor = "bg-secondary"; // Default color
              if (item.status === "空闲") bgColor = "bg-success";
              else if (item.status === "使用中") bgColor = "bg-danger";
              else if (item.status === "维护中") bgColor = "bg-warning";
              const count = Number(item.count) || 0;
              // Using col-md-4 for up to 3 items, adjust if more statuses
              deviceStatusHtml += `<div class="col-sm-4"><div class="p-3 ${bgColor} text-white rounded shadow-sm"><h5>${item.status}</h5><h3>${count}</h3></div></div>`;
            });
            deviceStatusHtml += '</div>';
            deviceChartContainer.innerHTML = deviceStatusHtml;
          }
        } else {
          if (totalDevicesEl) totalDevicesEl.textContent = 'N/A';
          if (availableDevicesEl) availableDevicesEl.textContent = 'N/A';
          if (deviceChartContainer) deviceChartContainer.innerHTML = '<p class="text-center text-danger">设备状态数据获取失败</p>';
        }

        // 处理和显示预约状态
        if (dashboard.reservation_status && Array.isArray(dashboard.reservation_status) && reservationChartContainer) {
          let reservationStatusHtml = '<div class="row text-center g-3">'; // Added g-3 for spacing
          dashboard.reservation_status.forEach(item => {
            let bgColor = "bg-dark"; // Default color
            if (item.status === "待审核") bgColor = "bg-info";
            else if (item.status === "已确认") bgColor = "bg-success";
            else if (item.status === "已取消") bgColor = "bg-danger";
            else if (item.status === "已完成") bgColor = "bg-secondary";
            const count = Number(item.count) || 0;
            // Using col-md-3 for up to 4 items, adjust if more statuses
            reservationStatusHtml += `<div class="col-sm-3"><div class="p-3 ${bgColor} text-white rounded shadow-sm"><h5>${item.status}</h5><h3>${count}</h3></div></div>`;
          });
          reservationStatusHtml += '</div>';
          reservationChartContainer.innerHTML = reservationStatusHtml;
        } else if (reservationChartContainer) {
          reservationChartContainer.innerHTML = '<p class="text-center text-danger">预约状态数据获取失败</p>';
        }

        // 处理和显示待处理维护数 (从 dashboard.maintenance_stats 获取)
        if (dashboard.maintenance_stats && pendingMaintenancesEl) {
          const pendingCount = Number(dashboard.maintenance_stats.total_pending_maintenances);
          // Check if pendingCount is a valid number (not NaN after Number conversion)
          if (!isNaN(pendingCount)) {
            pendingMaintenancesEl.textContent = pendingCount;
          } else {
            pendingMaintenancesEl.textContent = 'N/A'; // Or 0 if preferred
          }
        } else if (pendingMaintenancesEl) {
          pendingMaintenancesEl.textContent = 'N/A'; // Or 0
        }

      } else {
        // API status not 'success' or dashboard object missing
        console.error("仪表盘数据加载成功但格式不正确:", response.data);
        displayDashboardError(totalDevicesEl, availableDevicesEl, pendingMaintenancesEl, deviceChartContainer, reservationChartContainer);
      }
    })
    .catch(function (error) {
      console.error("加载仪表盘数据API请求失败:", error);
      displayDashboardError(totalDevicesEl, availableDevicesEl, pendingMaintenancesEl, deviceChartContainer, reservationChartContainer);
    });
}

function displayDashboardError(totalDevicesEl, availableDevicesEl, pendingMaintenancesEl, deviceChartContainer, reservationChartContainer) {
  if (totalDevicesEl) totalDevicesEl.textContent = '错误';
  if (availableDevicesEl) availableDevicesEl.textContent = '错误';
  if (pendingMaintenancesEl) pendingMaintenancesEl.textContent = '错误';
  if (deviceChartContainer) deviceChartContainer.innerHTML = '<p class="text-center text-danger">加载仪表盘设备状态出错</p>';
  if (reservationChartContainer) reservationChartContainer.innerHTML = '<p class="text-center text-danger">加载仪表盘预约状态出错</p>';
}

// 加载页面内容
function loadPage(pageName) {
  // 根据页面名称加载不同内容
  switch (pageName) {
    case "dashboard":
      // 首先确保仪表盘的HTML骨架已加载
      const pageContent = document.getElementById("page-content");
      if (pageContent) { // 确保 pageContent 存在
        pageContent.innerHTML = getDashboardHtmlSkeleton(); // 使用新函数设置HTML骨架
      }
      loadDashboard(); // 然后再调用 loadDashboard 来填充数据和图表
      break;
    case "devices":
      loadDevicesPage();
      break;
    case "rooms":
      loadRoomsPage();
      break;
    case "reservations":
      loadReservationsPage();
      break;
    case "maintenances":
      loadMaintenancesPage();
      break;
    case "users":
      loadUsersPage();
      break;
    case "statistics":
      loadStatisticsPage();
      break;
    case "audit":
      loadAuditPage();
      break;
    case "profile":
      loadProfilePage();
      break;
    default:
      loadDashboard();
  }
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return "";

  const date = new Date(dateTimeStr);

  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

// --- 设备管理页面 ---
function loadDevicesPage() {
  // 更新页面标题
  document.getElementById("page-title").textContent = "设备管理";

  // 更新页面操作按钮 (假设管理员角色)
  const pageActions = document.getElementById("page-actions");
  if (pageActions) {
    pageActions.innerHTML = `
            <button class="btn btn-primary" onclick="openDeviceModal()">
                <i class="bi bi-plus-circle"></i> 添加设备
            </button>
        `;
  }

  // 更新页面内容
  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="devices-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <div class="row">
                            <div class="col-md-6">
                                <h5 class="card-title mb-0">设备列表</h5>
                            </div>
                            <div class="col-md-6">
                                <div class="input-group">
                                    <input type="text" class="form-control" placeholder="搜索设备..." id="device-search">
                                    <button class="btn btn-outline-secondary" type="button" id="device-search-btn">
                                        <i class="bi bi-search"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>设备ID</th>
                                        <th>设备名称</th>
                                        <th>设备类型</th>
                                        <th>所在机房</th>
                                        <th>状态</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody id="devices-table-body">
                                    <tr>
                                        <td colspan="6" class="text-center">加载中...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;

    // 加载设备数据
    loadDevicesData();
  }
}

// 加载设备数据
function loadDevicesData() {
  const tableBody = document.getElementById("devices-table-body");
  axios
    .get("/api/devices/details") // 使用获取详细信息的接口
    .then(function (response) {
      if (response.data.status === "success") {
        const devices = response.data.device_details;
        let html = "";
        devices.forEach((device) => {
          let statusClass = "";
          switch (device.status) {
            case "空闲":
              statusClass = "bg-success";
              break;
            case "使用中":
              statusClass = "bg-danger";
              break;
            case "维护中":
              statusClass = "bg-warning";
              break;
            default:
              statusClass = "bg-secondary";
          }

          html += `
                    <tr>
                        <td>${device.did}</td>
                        <td>${device.dname}</td>
                        <td>${device.type}</td>
                        <td>${device.location || "未分配"}</td>
                        <td><span class="badge ${statusClass} text-white">${device.status}</span></td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="viewDevice(${device.did})">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-primary" onclick="openDeviceModal(${device.did})">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteDevice(${device.did})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
        });
        tableBody.innerHTML = html;

        // 添加搜索功能
        addTableSearch("device-search-btn", "device-search", tableBody);
      } else {
        tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">加载设备失败: ${response.data.message}</td></tr>`;
      }
    })
    .catch(function (error) {
      console.error("加载设备数据失败:", error);
      tableBody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">加载设备失败，请检查网络或联系管理员</td></tr>`;
    });
}

// 打开设备模态框 (添加/编辑)
function openDeviceModal(did = null) {
  const modalTitle = document.getElementById("modal-title");
  const modalBody = document.getElementById("modal-body");
  const modalSubmit = document.getElementById("modal-submit");

  modalTitle.textContent = did ? "编辑设备" : "添加设备";
  modalBody.innerHTML = `
        <form id="device-form">
            <input type="hidden" id="device-id" value="${did || ''}">
            <div class="mb-3">
                <label for="device-name" class="form-label">设备名称</label>
                <input type="text" class="form-control" id="device-dname" required>
            </div>
            <div class="mb-3">
                <label for="device-type" class="form-label">设备类型</label>
                <input type="text" class="form-control" id="device-type" required>
            </div>
            <div class="mb-3">
                <label for="device-room_id" class="form-label">所在机房</label>
                <select class="form-select" id="device-room_id">
                    <option value="">请选择机房</option>
                    <!-- 机房选项将动态加载 -->
                </select>
            </div>
            <div class="mb-3">
                <label for="device-status" class="form-label">状态</label>
                <select class="form-select" id="device-status">
                    <option value="空闲">空闲</option>
                    <option value="使用中">使用中</option>
                    <option value="维护中">维护中</option>
                </select>
            </div>
        </form>
    `;

  // 加载机房选项
  const roomSelect = document.getElementById("device-room_id");
  axios.get("/api/rooms").then(response => {
      if (response.data.status === 'success') {
          response.data.rooms.forEach(room => {
              roomSelect.innerHTML += `<option value="${room.rid}">${room.location}</option>`;
          });
      }
  });

  // 如果是编辑，加载现有数据
  if (did) {
    axios.get(`/api/devices/${did}`).then(response => {
        if (response.data.status === 'success') {
            const device = response.data.device;
            document.getElementById('device-dname').value = device.dname;
            document.getElementById('device-type').value = device.type;
            document.getElementById('device-room_id').value = device.room_id || '';
            document.getElementById('device-status').value = device.status;
        }
    });
  }

  modalSubmit.onclick = function () {
    submitDeviceForm(did);
  };

  const formModal = new bootstrap.Modal(document.getElementById("form-modal"));
  formModal.show();
}

// 提交设备表单
function submitDeviceForm(did) {
  const deviceName = document.getElementById("device-dname").value;
  const deviceType = document.getElementById("device-type").value;
  const roomId = document.getElementById("device-room_id").value;
  const deviceStatus = document.getElementById("device-status").value;

  // 如果未选择机房 (假设其值为 ""), 则发送 null，否则发送所选值
  // 后端要求 room_id 必须存在且有效，所以如果业务允许无机房设备，后端也需调整
  const payloadRoomId = roomId === "" ? null : roomId;

  const data = { 
    dname: deviceName,    // 使用 dname
    type: deviceType,
    room_id: payloadRoomId, // 使用 room_id
    status: deviceStatus 
  };
  const url = did ? `/api/devices/${did}` : "/api/devices";
  const method = did ? "put" : "post";

  axios({
    method: method,
    url: url,
    data: data,
  })
    .then(function (response) {
      if (response.data.status === "success") {
        alert(did ? "设备更新成功" : "设备添加成功");
        bootstrap.Modal.getInstance(document.getElementById("form-modal")).hide();
        loadDevicesData(); // 重新加载数据
      } else {
        alert("操作失败: " + response.data.message);
      }
    })
    .catch(function (error) {
      console.error("设备操作失败:", error);
      alert("操作失败，请检查网络或联系管理员");
    });
}

// 查看设备详情
function viewDevice(did) {
  alert(`查看设备详情功能尚未实现：设备ID ${did}`);
}

// 删除设备
function deleteDevice(did) {
  if (confirm(`确定要删除设备ID为 ${did} 的设备吗？`)) {
    axios
      .delete(`/api/devices/${did}`)
      .then(function (response) {
        if (response.data.status === "success") {
          alert(`设备ID ${did} 已删除`);
          loadDevicesData(); // 重新加载数据
        } else {
          alert("删除失败: " + response.data.message);
        }
      })
      .catch(function (error) {
        console.error("删除设备失败:", error);
        alert("删除失败，请检查网络或联系管理员");
      });
  }
}

// --- 机房管理页面 ---
function loadRoomsPage() {
  document.getElementById("page-title").textContent = "机房管理";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) {
    pageActions.innerHTML = `
            <button class="btn btn-primary" onclick="openRoomModal()">
                <i class="bi bi-plus-circle"></i> 添加机房
            </button>
        `;
  }

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="rooms-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">机房列表</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>机房ID</th>
                                        <th>位置</th>
                                        <th>容量</th>
                                        <th>开放时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody id="rooms-table-body">
                                    <tr><td colspan="5" class="text-center">加载中...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    loadRoomsData();
  }
}

function loadRoomsData() {
  const tableBody = document.getElementById("rooms-table-body");
  axios.get("/api/rooms")
    .then(response => {
      if (response.data.status === 'success') {
        const rooms = response.data.rooms;
        let html = '';
        rooms.forEach(room => {
          html += `
            <tr>
              <td>${room.rid}</td>
              <td>${room.location}</td>
              <td>${room.capacity}</td>
              <td>${room.open_time}</td>
              <td>
                <button class="btn btn-sm btn-primary" onclick="openRoomModal(${room.rid})">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteRoom(${room.rid})">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          `;
        });
        tableBody.innerHTML = html;
      } else {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">加载机房失败: ${response.data.message}</td></tr>`;
      }
    })
    .catch(error => {
      console.error("加载机房数据失败:", error);
      tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">加载机房失败，请检查网络或联系管理员</td></tr>`;
    });
}

function openRoomModal(rid = null) {
  const modalTitle = document.getElementById("modal-title");
  const modalBody = document.getElementById("modal-body");
  const modalSubmit = document.getElementById("modal-submit");

  modalTitle.textContent = rid ? "编辑机房" : "添加机房";
  modalBody.innerHTML = `
    <form id="room-form">
      <input type="hidden" id="room-id" value="${rid || ''}">
      <div class="mb-3">
        <label for="room-location" class="form-label">位置</label>
        <input type="text" class="form-control" id="room-location" required>
      </div>
      <div class="mb-3">
        <label for="room-capacity" class="form-label">容量</label>
        <input type="number" class="form-control" id="room-capacity" required>
      </div>
      <div class="mb-3">
        <label for="room-open-time" class="form-label">开放时间</label>
        <input type="text" class="form-control" id="room-open-time" placeholder="例如: 周一至周五 8:00-22:00" required>
      </div>
    </form>
  `;

  if (rid) {
    axios.get(`/api/rooms/${rid}`).then(response => {
      if (response.data.status === 'success') {
        const room = response.data.room;
        document.getElementById('room-location').value = room.location;
        document.getElementById('room-capacity').value = room.capacity;
        document.getElementById('room-open-time').value = room.open_time;
      }
    });
  }

  modalSubmit.onclick = function () {
    submitRoomForm(rid);
  };

  const formModal = new bootstrap.Modal(document.getElementById("form-modal"));
  formModal.show();
}

function submitRoomForm(rid) {
  const location = document.getElementById("room-location").value;
  const capacity = document.getElementById("room-capacity").value;
  const open_time = document.getElementById("room-open-time").value;

  const data = { location, capacity, open_time };
  const url = rid ? `/api/rooms/${rid}` : "/api/rooms";
  const method = rid ? "put" : "post";

  axios({ method, url, data })
    .then(response => {
      if (response.data.status === 'success') {
        alert(rid ? "机房更新成功" : "机房添加成功");
        bootstrap.Modal.getInstance(document.getElementById("form-modal")).hide();
        loadRoomsData();
      } else {
        alert("操作失败: " + response.data.message);
      }
    })
    .catch(error => {
      console.error("机房操作失败:", error);
      alert("操作失败，请检查网络或联系管理员");
    });
}

function deleteRoom(rid) {
  if (confirm(`确定要删除机房ID为 ${rid} 的机房吗？`)) {
    axios.delete(`/api/rooms/${rid}`)
      .then(response => {
        if (response.data.status === 'success') {
          alert(`机房ID ${rid} 已删除`);
          loadRoomsData();
        } else {
          alert("删除失败: " + response.data.message);
        }
      })
      .catch(error => {
        console.error("删除机房失败:", error);
        alert("删除失败，请检查网络或联系管理员");
      });
  }
}

// --- 预约管理页面 ---
function loadReservationsPage() {
  document.getElementById("page-title").textContent = "预约管理";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) {
    pageActions.innerHTML = `
            <button class="btn btn-primary" onclick="openReservationModal()">
                <i class="bi bi-plus-circle"></i> 发起预约
            </button>
        `;
  }

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="reservations-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">预约列表</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>预约ID</th>
                                        <th>用户</th>
                                        <th>设备</th>
                                        <th>开始时间</th>
                                        <th>结束时间</th>
                                        <th>状态</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody id="reservations-table-body">
                                    <tr><td colspan="7" class="text-center">加载中...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    loadReservationsData();
  }
}

function loadReservationsData() {
  const tableBody = document.getElementById("reservations-table-body");
  axios.get("/api/reservations") // 获取详细预约信息
    .then(response => {
      if (response.data.status === 'success') {
        const reservations = response.data.reservations;
        let html = '';
        reservations.forEach(res => {
          let statusClass = '';
          switch (res.status) {
            case '待审核': statusClass = 'bg-info'; break;
            case '已确认': statusClass = 'bg-success'; break;
            case '已取消': statusClass = 'bg-secondary'; break;
            case '已完成': statusClass = 'bg-primary'; break;
            default: statusClass = 'bg-dark';
          }
          html += `
            <tr>
              <td>${res.res_id}</td>
              <td>${res.user_name || res.uid}</td>
              <td>${res.device_name || res.did}</td>
              <td>${formatDateTime(res.start_time)}</td>
              <td>${formatDateTime(res.end_time)}</td>
              <td><span class="badge ${statusClass} text-white">${res.status}</span></td>
              <td>
                ${res.status === '待审核' ? 
                  `<button class="btn btn-sm btn-success" onclick="updateReservationStatus(${res.res_id}, '已确认')"><i class="bi bi-check-circle"></i></button>
                   <button class="btn btn-sm btn-danger" onclick="updateReservationStatus(${res.res_id}, '已取消')"><i class="bi bi-x-circle"></i></button>` : ''}
                ${res.status !== '已取消' && res.status !== '已完成' ? 
                  `<button class="btn btn-sm btn-secondary" onclick="updateReservationStatus(${res.res_id}, '已取消')"><i class="bi bi-calendar-x"></i></button>` : ''}
              </td>
            </tr>
          `;
        });
        tableBody.innerHTML = html;
      } else {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">加载预约失败: ${response.data.message}</td></tr>`;
      }
    })
    .catch(error => {
      console.error("加载预约数据失败:", error);
      tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">加载预约失败，请检查网络或联系管理员</td></tr>`;
    });
}

function openReservationModal() {
  const modalTitle = document.getElementById("modal-title");
  const modalBody = document.getElementById("modal-body");
  const modalSubmit = document.getElementById("modal-submit");

  modalTitle.textContent = "发起预约";
  modalBody.innerHTML = `
    <form id="reservation-form">
      <div class="mb-3">
        <label for="reservation-did" class="form-label">选择设备</label>
        <select class="form-select" id="reservation-did" required>
          <option value="">请选择可用设备</option>
          <!-- 设备选项将动态加载 -->
        </select>
      </div>
      <div class="mb-3">
        <label for="reservation-start-time" class="form-label">开始时间</label>
        <input type="datetime-local" class="form-control" id="reservation-start-time" required>
      </div>
      <div class="mb-3">
        <label for="reservation-end-time" class="form-label">结束时间</label>
        <input type="datetime-local" class="form-control" id="reservation-end-time" required>
      </div>
    </form>
  `;

  // 加载可用设备选项
  const deviceSelect = document.getElementById("reservation-did");
  axios.get("/api/devices?status=空闲").then(response => {
      if (response.data.status === 'success') {
          response.data.devices.forEach(device => {
              deviceSelect.innerHTML += `<option value="${device.did}">${device.dname} (${device.type})</option>`;
          });
      }
  });

  modalSubmit.onclick = submitReservationForm;

  const formModal = new bootstrap.Modal(document.getElementById("form-modal"));
  formModal.show();
}

function submitReservationForm() {
  const did = document.getElementById("reservation-did").value;
  const startTime = document.getElementById("reservation-start-time").value;
  const endTime = document.getElementById("reservation-end-time").value;

  if (!did || !startTime || !endTime) {
      alert("请填写所有必填项");
      return;
  }

  // 格式化时间为 YYYY-MM-DD HH:MM:SS
  const formattedStartTime = startTime.replace("T", " ") + ":00";
  const formattedEndTime = endTime.replace("T", " ") + ":00";

  const data = { did, start_time: formattedStartTime, end_time: formattedEndTime };

  axios.post("/api/reservations", data)
    .then(response => {
      if (response.data.status === 'success') {
        alert("预约发起成功，等待审核");
        bootstrap.Modal.getInstance(document.getElementById("form-modal")).hide();
        loadReservationsData();
      } else {
        alert("预约失败: " + response.data.message);
      }
    })
    .catch(error => {
      console.error("预约失败:", error);
      alert("预约失败: " + (error.response?.data?.message || "请检查网络或联系管理员"));
    });
}

function updateReservationStatus(resId, status) {
  axios.put(`/api/reservations/${resId}/status`, { status })
    .then(response => {
      if (response.data.status === 'success') {
        alert(`预约状态更新为 ${status} 成功`);
        loadReservationsData();
      } else {
        alert("状态更新失败: " + response.data.message);
      }
    })
    .catch(error => {
      console.error("更新预约状态失败:", error);
      alert("状态更新失败，请检查网络或联系管理员");
    });
}

// --- 维护管理页面 ---
function loadMaintenancesPage() {
  document.getElementById("page-title").textContent = "维护管理";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) {
    pageActions.innerHTML = `
            <button class="btn btn-warning" onclick="openMaintenanceModal()">
                <i class="bi bi-tools"></i> 报修设备
            </button>
        `;
  }

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="maintenances-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">维护记录</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>记录ID</th>
                                        <th>设备</th>
                                        <th>问题描述</th>
                                        <th>报修时间</th>
                                        <th>处理人</th>
                                        <th>状态</th>
                                        <th>完成时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody id="maintenances-table-body">
                                    <tr><td colspan="8" class="text-center">加载中...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    loadMaintenancesData();
  }
}

function loadMaintenancesData() {
  const tableBody = document.getElementById("maintenances-table-body");
  axios.get("/api/maintenances") // 获取详细维护信息
    .then(response => {
      if (response.data.status === 'success') {
        const maintenances = response.data.maintenances;
        let html = '';
        maintenances.forEach(maint => {
          let statusClass = '';
          switch (maint.status) {
            case '待处理': statusClass = 'bg-warning'; break;
            case '处理中': statusClass = 'bg-info'; break;
            case '已完成': statusClass = 'bg-success'; break;
            default: statusClass = 'bg-secondary';
          }
          html += `
            <tr>
              <td>${maint.mid}</td>
              <td>${maint.device_name || maint.did}</td>
              <td>${maint.issue}</td>
              <td>${formatDateTime(maint.report_time)}</td>
              <td>${maint.handler || '-'}</td>
              <td><span class="badge ${statusClass} text-white">${maint.status}</span></td>
              <td>${maint.complete_time ? formatDateTime(maint.complete_time) : '-'}</td>
              <td>
                ${maint.status === '待处理' ? 
                  `<button class="btn btn-sm btn-primary" onclick="updateMaintenanceStatus(${maint.mid}, '处理中')">开始处理</button>` : ''}
                ${maint.status === '处理中' ? 
                  `<button class="btn btn-sm btn-success" onclick="updateMaintenanceStatus(${maint.mid}, '已完成')">标记完成</button>` : ''}
              </td>
            </tr>
          `;
        });
        tableBody.innerHTML = html;
      } else {
        tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">加载维护记录失败: ${response.data.message}</td></tr>`;
      }
    })
    .catch(error => {
      console.error("加载维护数据失败:", error);
      tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">加载维护记录失败，请检查网络或联系管理员</td></tr>`;
    });
}

function openMaintenanceModal() {
  const modalTitle = document.getElementById("modal-title");
  const modalBody = document.getElementById("modal-body");
  const modalSubmit = document.getElementById("modal-submit");

  modalTitle.textContent = "报修设备";
  modalBody.innerHTML = `
    <form id="maintenance-form">
      <div class="mb-3">
        <label for="maintenance-did" class="form-label">选择设备</label>
        <select class="form-select" id="maintenance-did" required>
          <option value="">请选择需要报修的设备</option>
          <!-- 设备选项将动态加载 -->
        </select>
      </div>
      <div class="mb-3">
        <label for="maintenance-issue" class="form-label">问题描述</label>
        <textarea class="form-control" id="maintenance-issue" rows="3" required></textarea>
      </div>
    </form>
  `;

  // 加载所有设备选项
  const deviceSelect = document.getElementById("maintenance-did");
  axios.get("/api/devices/details").then(response => {
      if (response.data.status === 'success') {
          response.data.device_details.forEach(device => {
              deviceSelect.innerHTML += `<option value="${device.did}">${device.dname} (${device.type}) - ${device.location || '未分配'}</option>`;
          });
      }
  });

  modalSubmit.onclick = submitMaintenanceForm;

  const formModal = new bootstrap.Modal(document.getElementById("form-modal"));
  formModal.show();
}

function submitMaintenanceForm() {
  const did = document.getElementById("maintenance-did").value;
  const issue = document.getElementById("maintenance-issue").value;

  if (!did || !issue) {
      alert("请选择设备并描述问题");
      return;
  }

  const data = { did, issue };

  axios.post("/api/maintenances", data)
    .then(response => {
      if (response.data.status === 'success') {
        alert("报修成功");
        bootstrap.Modal.getInstance(document.getElementById("form-modal")).hide();
        loadMaintenancesData();
        loadDevicesData(); // 刷新设备列表状态
      } else {
        alert("报修失败: " + response.data.message);
      }
    })
    .catch(error => {
      console.error("报修失败:", error);
      alert("报修失败: " + (error.response?.data?.message || "请检查网络或联系管理员"));
    });
}

function updateMaintenanceStatus(mid, status) {
  // 假设处理人是当前用户，实际应从后端获取或让用户输入
  const handler = "管理员"; 
  axios.put(`/api/maintenances/${mid}/status`, { status, handler })
    .then(response => {
      if (response.data.status === 'success') {
        alert(`维护状态更新为 ${status} 成功`);
        loadMaintenancesData();
        loadDevicesData(); // 刷新设备列表状态
      } else {
        alert("状态更新失败: " + response.data.message);
      }
    })
    .catch(error => {
      console.error("更新维护状态失败:", error);
      alert("状态更新失败，请检查网络或联系管理员");
    });
}

// --- 用户管理页面 ---
function loadUsersPage() {
  document.getElementById("page-title").textContent = "用户管理";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) {
    pageActions.innerHTML = `
            <button class="btn btn-primary" onclick="openUserModal()">
                <i class="bi bi-person-plus"></i> 添加用户
            </button>
        `;
  }

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="users-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">用户列表</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>用户ID</th>
                                        <th>姓名</th>
                                        <th>学号/工号</th>
                                        <th>角色</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody id="users-table-body">
                                    <tr><td colspan="5" class="text-center">加载中...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    loadUsersData();
  }
}

function loadUsersData() {
  const tableBody = document.getElementById("users-table-body");
  axios.get("/api/auth/users")
    .then(response => {
      if (response.data.status === 'success') {
        const users = response.data.users;
        let html = '';
        users.forEach(user => {
          html += `
            <tr>
              <td>${user.uid}</td>
              <td>${user.uname}</td>
              <td>${user.code}</td>
              <td>${user.role}</td>
              <td>
                <button class="btn btn-sm btn-primary" onclick="openUserModal(${user.uid})">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.uid})">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          `;
        });
        tableBody.innerHTML = html;
      } else {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">加载用户失败: ${response.data.message}</td></tr>`;
      }
    })
    .catch(error => {
      console.error("加载用户数据失败:", error);
      tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">加载用户失败，请检查网络或联系管理员</td></tr>`;
    });
}

function openUserModal(uid = null) {
  const modalTitle = document.getElementById("modal-title");
  const modalBody = document.getElementById("modal-body");
  const modalSubmit = document.getElementById("modal-submit");

  modalTitle.textContent = uid ? "编辑用户" : "添加用户";
  modalBody.innerHTML = `
    <form id="user-form">
      <input type="hidden" id="user-id" value="${uid || ''}">
      <div class="mb-3">
        <label for="user-name" class="form-label">姓名</label>
        <input type="text" class="form-control" id="user-name" required>
      </div>
      <div class="mb-3">
        <label for="user-code" class="form-label">学号/工号</label>
        <input type="text" class="form-control" id="user-code" required>
      </div>
      <div class="mb-3">
        <label for="user-password" class="form-label">密码 ${uid ? '(留空表示不修改)' : ''}</label>
        <input type="password" class="form-control" id="user-password" ${uid ? '' : 'required'}>
      </div>
      <div class="mb-3">
        <label for="user-role" class="form-label">角色</label>
        <select class="form-select" id="user-role" required>
          <option value="学生">学生</option>
          <option value="教师">教师</option>
          <option value="管理员">管理员</option>
        </select>
      </div>
    </form>
  `;

  if (uid) {
    axios.get(`/api/auth/users/${uid}`).then(response => {
      if (response.data.status === 'success') {
        const user = response.data.user;
        document.getElementById('user-name').value = user.uname;
        document.getElementById('user-code').value = user.code;
        document.getElementById('user-role').value = user.role;
      }
    });
  }

  modalSubmit.onclick = function () {
    submitUserForm(uid);
  };

  const formModal = new bootstrap.Modal(document.getElementById("form-modal"));
  formModal.show();
}

function submitUserForm(uid) {
  const uname = document.getElementById("user-name").value;
  const code = document.getElementById("user-code").value;
  const password = document.getElementById("user-password").value;
  const role = document.getElementById("user-role").value;

  const data = { uname, code, role };
  if (password) {
      data.password = password;
  }
  
  const url = uid ? `/api/auth/users/${uid}` : "/api/auth/register"; // 使用注册接口添加用户
  const method = uid ? "put" : "post";

  axios({ method, url, data })
    .then(response => {
      if (response.data.status === 'success') {
        alert(uid ? "用户更新成功" : "用户添加成功");
        bootstrap.Modal.getInstance(document.getElementById("form-modal")).hide();
        loadUsersData();
      } else {
        alert("操作失败: " + response.data.message);
      }
    })
    .catch(error => {
      console.error("用户操作失败:", error);
      alert("操作失败: " + (error.response?.data?.message || "请检查网络或联系管理员"));
    });
}

function deleteUser(uid) {
  if (confirm(`确定要删除用户ID为 ${uid} 的用户吗？`)) {
    axios.delete(`/api/auth/users/${uid}`)
      .then(response => {
        if (response.data.status === 'success') {
          alert(`用户ID ${uid} 已删除`);
          loadUsersData();
        } else {
          alert("删除失败: " + response.data.message);
        }
      })
      .catch(error => {
        console.error("删除用户失败:", error);
        alert("删除失败，请检查网络或联系管理员");
      });
  }
}

// --- 统计分析页面 ---
function loadStatisticsPage() {
  document.getElementById("page-title").textContent = "统计分析";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) pageActions.innerHTML = ''; // 清空操作按钮

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="statistics-page">
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">设备使用率</div>
                            <div class="card-body" id="stats-device-usage">加载中...</div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">机房使用率</div>
                            <div class="card-body" id="stats-room-usage">加载中...</div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">按角色统计设备使用率</div>
                            <div class="card-body" id="stats-user-role">加载中...</div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header">维护统计</div>
                            <div class="card-body" id="stats-maintenance">加载中...</div>
                        </div>
                    </div>
                </div>
                 <div class="row">
                    <div class="col-12 mb-4">
                        <div class="card h-100">
                            <div class="card-header">月度使用趋势</div>
                            <div class="card-body" style="height: 400px; overflow: auto;"><canvas id="monthly-usage-chart"></canvas></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    loadStatisticsData();
  }
}

function loadStatisticsData() {
    // 加载设备使用率
    axios.get('/api/stats/device_usage').then(res => {
        const container = document.getElementById('stats-device-usage');
        if (res.data.status === 'success' && Array.isArray(res.data.device_usage_stats)) {
            let html = '<ul class="list-group list-group-flush">';
            if (res.data.device_usage_stats.length === 0) {
                html += '<li class="list-group-item text-center">暂无设备使用数据</li>';
            } else {
                res.data.device_usage_stats.forEach(item => {
                    const deviceName = item.dname || '未知设备';
                    const usageCount = Number(item.reservation_count) || 0;
                    const totalHours = Number(item.total_hours_used) || 0;
                    html += `<li class="list-group-item d-flex justify-content-between align-items-center">${deviceName} <span class="badge bg-primary rounded-pill">${usageCount}次 / ${totalHours.toFixed(1)}小时</span></li>`;
                });
            }
            html += '</ul>';
            container.innerHTML = html;
        } else {
            console.error("加载设备使用率失败或数据格式不正确:", res.data);
            container.innerHTML = '<p class="text-danger">加载失败</p>';
        }
    }).catch(err => {
        console.error("请求设备使用率API失败:", err);
        document.getElementById('stats-device-usage').innerHTML = '<p class="text-danger">加载失败</p>';
    });

    // 加载机房使用率
    axios.get('/api/stats/room_usage').then(res => {
        const container = document.getElementById('stats-room-usage');
        if (res.data.status === 'success' && Array.isArray(res.data.room_usage_stats)) {
            let html = '<ul class="list-group list-group-flush">';
            if (res.data.room_usage_stats.length === 0) {
                html += '<li class="list-group-item text-center">暂无机房使用数据</li>';
            } else {
                res.data.room_usage_stats.forEach(item => {
                    const roomLocation = item.location || '未知机房';
                    const usageCount = Number(item.reservation_count) || 0;
                    const uniqueUsers = Number(item.unique_users) || 0;
                    html += `<li class="list-group-item d-flex justify-content-between align-items-center">${roomLocation} <span class="badge bg-info rounded-pill">${usageCount}次预约 / ${uniqueUsers}独立用户</span></li>`;
                });
            }
            html += '</ul>';
            container.innerHTML = html;
        } else {
            console.error("加载机房使用率失败或数据格式不正确:", res.data);
            container.innerHTML = '<p class="text-danger">加载失败</p>';
        }
    }).catch(err => {
        console.error("请求机房使用率API失败:", err);
        document.getElementById('stats-room-usage').innerHTML = '<p class="text-danger">加载失败</p>';
    });

    // 加载角色使用率
    axios.get('/api/stats/user_role').then(res => {
        const container = document.getElementById('stats-user-role');
        if (res.data.status === 'success' && Array.isArray(res.data.user_role_stats)) {
            let html = '<ul class="list-group list-group-flush">';
            if (res.data.user_role_stats.length === 0) {
                html += '<li class="list-group-item text-center">暂无用户角色使用数据</li>';
            } else {
                res.data.user_role_stats.forEach(item => {
                    const role = item.role || '未知角色';
                    const usageCount = Number(item.reservation_count) || 0;
                    const avgHours = Number(item.avg_hours) || 0;
                    html += `<li class="list-group-item d-flex justify-content-between align-items-center">${role} <span class="badge bg-warning rounded-pill">${usageCount}次预约 / 平均${avgHours.toFixed(1)}小时</span></li>`;
                });
            }
            html += '</ul>';
            container.innerHTML = html;
        } else {
            console.error("加载角色使用率失败或数据格式不正确:", res.data);
            container.innerHTML = '<p class="text-danger">加载失败</p>';
        }
    }).catch(err => {
        console.error("请求角色使用率API失败:", err);
        document.getElementById('stats-user-role').innerHTML = '<p class="text-danger">加载失败</p>';
    });

    // 加载维护统计
    axios.get('/api/stats/maintenance').then(res => {
        const container = document.getElementById('stats-maintenance');
        if (res.data.status === 'success' && res.data.maintenance_stats) {
            const stats = res.data.maintenance_stats;
            const totalCompleted = Number(stats.total_completed_maintenances) || 0;
            const pendingCount = Number(stats.total_pending_maintenances) || 0;
            const avgHandleTime = Number(stats.average_completion_time_hours);

            container.innerHTML = `
                <p>总已完成维护: ${totalCompleted}次</p>
                <p>平均处理时长: ${!isNaN(avgHandleTime) && avgHandleTime !== null ? avgHandleTime.toFixed(1) + '小时' : 'N/A'}</p>
                <p>当前待处理: ${pendingCount}项</p>
            `;
        } else {
            console.error("加载维护统计失败或数据格式不正确:", res.data);
            container.innerHTML = '<p class="text-danger">加载失败</p>';
        }
    }).catch(err => {
        console.error("请求维护统计API失败:", err);
        document.getElementById('stats-maintenance').innerHTML = '<p class="text-danger">加载失败</p>';
    });
    
    // 加载月度趋势图表
    axios.get('/api/stats/monthly_usage').then(res => {
        const chartCanvas = document.getElementById('monthly-usage-chart');
        if (res.data.status === 'success' && Array.isArray(res.data.monthly_usage_trend)) {
            if (res.data.monthly_usage_trend.length === 0 && chartCanvas) {
                chartCanvas.outerHTML = '<p class="text-center">暂无月度使用趋势数据</p>';
            } else if (chartCanvas) {
                updateMonthlyUsageChart(res.data.monthly_usage_trend);
            }
        } else {
            console.error("加载月度趋势失败或数据格式不正确:", res.data);
             if(chartCanvas) chartCanvas.outerHTML = '<p class="text-danger text-center">月度趋势加载失败</p>';
        }
    }).catch(err => {
        const chartCanvas = document.getElementById('monthly-usage-chart');
        console.error("请求月度趋势API失败:", err);
        if(chartCanvas) chartCanvas.outerHTML = '<p class="text-danger text-center">月度趋势加载失败</p>';
    });
}

// 更新月度使用趋势图表
let monthlyUsageChart = null;
function updateMonthlyUsageChart(monthlyUsage) {
    const ctx = document.getElementById('monthly-usage-chart')?.getContext('2d');
    if (!ctx) return;

    if (monthlyUsageChart) {
        monthlyUsageChart.destroy();
        monthlyUsageChart = null; // 显式置为null
    }

    const labels = monthlyUsage.map(item => item.month);
    const reservationCounts = monthlyUsage.map(item => item.reservation_count);
    const totalHours = monthlyUsage.map(item => item.total_hours);

    monthlyUsageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '预约次数',
                    data: reservationCounts,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: '使用总时长(小时)',
                    data: totalHours,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // 确保动画是关闭的
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '预约次数'
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: '使用总时长(小时)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// --- 审计日志页面 ---
function loadAuditPage() {
  document.getElementById("page-title").textContent = "审计日志";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) pageActions.innerHTML = ''; // 清空操作按钮

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="audit-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">操作日志</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>日志ID</th>
                                        <th>用户</th>
                                        <th>操作类型</th>
                                        <th>目标表</th>
                                        <th>操作内容</th>
                                        <th>IP地址</th>
                                        <th>时间</th>
                                    </tr>
                                </thead>
                                <tbody id="audit-table-body">
                                    <tr><td colspan="7" class="text-center">加载中...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    loadAuditData();
  }
}

function loadAuditData() {
  const tableBody = document.getElementById("audit-table-body");
  axios.get("/api/audit/audit_logs")
    .then(response => {
      if (response.data.status === 'success') {
        const logs = response.data.audit_logs;
        let html = '';
        logs.forEach(log => {
          html += `
            <tr>
              <td>${log.log_id}</td>
              <td>${log.user_name || log.uid}</td>
              <td>${log.action}</td>
              <td>${log.target_table}</td>
              <td>${log.sql_text}</td>
              <td>${log.ip_address}</td>
              <td>${formatDateTime(log.log_time)}</td>
            </tr>
          `;
        });
        tableBody.innerHTML = html;
      } else {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">加载审计日志失败: ${response.data.message}</td></tr>`;
      }
    })
    .catch(error => {
      console.error("加载审计日志失败:", error);
      tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">加载审计日志失败，请检查网络或联系管理员</td></tr>`;
    });
}

// --- 个人信息页面 ---
function loadProfilePage() {
  document.getElementById("page-title").textContent = "个人信息";
  const pageActions = document.getElementById("page-actions");
  if (pageActions) pageActions.innerHTML = ''; // 清空操作按钮

  const pageContent = document.getElementById("page-content");
  if (pageContent) {
    pageContent.innerHTML = `
            <div id="profile-page">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">我的信息</h5>
                    </div>
                    <div class="card-body" id="profile-details">
                        加载中...
                    </div>
                </div>
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title mb-0">修改密码</h5>
                    </div>
                    <div class="card-body">
                        <form id="change-password-form">
                            <div class="mb-3">
                                <label for="current-password" class="form-label">当前密码</label>
                                <input type="password" class="form-control" id="current-password" required>
                            </div>
                            <div class="mb-3">
                                <label for="new-password" class="form-label">新密码</label>
                                <input type="password" class="form-control" id="new-password" required>
                            </div>
                            <div class="mb-3">
                                <label for="confirm-password" class="form-label">确认新密码</label>
                                <input type="password" class="form-control" id="confirm-password" required>
                            </div>
                            <button type="submit" class="btn btn-primary">确认修改</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    loadProfileData();
    addChangePasswordHandler();
  }
}

function loadProfileData() {
  const profileDetails = document.getElementById("profile-details");
  axios.get("/api/auth/profile")
    .then(response => {
      if (response.data.status === 'success') {
        const user = response.data.user;
        profileDetails.innerHTML = `
          <p><strong>姓名:</strong> ${user.uname}</p>
          <p><strong>学号/工号:</strong> ${user.code}</p>
          <p><strong>角色:</strong> ${user.role}</p>
        `;
      } else {
        profileDetails.innerHTML = `<p class="text-danger">加载个人信息失败: ${response.data.message}</p>`;
      }
    })
    .catch(error => {
      console.error("加载个人信息失败:", error);
      profileDetails.innerHTML = `<p class="text-danger">加载个人信息失败，请检查网络或联系管理员</p>`;
    });
}

function addChangePasswordHandler() {
    const form = document.getElementById('change-password-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const currentPassword = document.getElementById('current-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (newPassword !== confirmPassword) {
            alert('新密码和确认密码不一致');
            return;
        }

        axios.put('/api/auth/profile/password', {
            current_password: currentPassword,
            new_password: newPassword
        })
        .then(response => {
            if (response.data.status === 'success') {
                alert('密码修改成功');
                form.reset();
            } else {
                alert('密码修改失败: ' + response.data.message);
            }
        })
        .catch(error => {
            console.error('修改密码失败:', error);
            alert('密码修改失败: ' + (error.response?.data?.message || '请检查网络或联系管理员'));
        });
    });
}

// --- 通用函数 ---
// 添加表格搜索功能
function addTableSearch(buttonId, inputId, tableBody) {
    const searchButton = document.getElementById(buttonId);
    const searchInput = document.getElementById(inputId);
    if (searchButton && searchInput && tableBody) {
        searchButton.addEventListener('click', function() {
            const searchText = searchInput.value.toLowerCase();
            const rows = tableBody.querySelectorAll('tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchText)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
        // 支持回车搜索
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchButton.click();
            }
        });
    }
}

function getDashboardHtmlSkeleton() {
    // 这个函数返回仪表盘页面的基础HTML结构字符串
    // 这个HTML结构必须包含 id="total-devices", "available-devices", 
    // "pending-maintenances", "device-status-chart-container", 
    // "reservation-status-chart-container" 等元素。
    return `
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-white bg-primary shadow-sm">
                    <div class="card-header">设备总数</div>
                    <div class="card-body text-center">
                        <h2 class="card-title" id="total-devices">...</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-success shadow-sm">
                    <div class="card-header">可用设备</div>
                    <div class="card-body text-center">
                        <h2 class="card-title" id="available-devices">...</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-warning shadow-sm">
                    <div class="card-header">待处理维护</div>
                    <div class="card-body text-center">
                        <h2 class="card-title" id="pending-maintenances">...</h2>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-6 mb-4">
                <div class="card shadow-sm">
                    <div class="card-header">
                        <i class="bi bi-pie-chart-fill me-1"></i>
                        设备状态分布
                    </div>
                    <div class="card-body" id="device-status-chart-container" style="min-height: 200px;">
                        <p class="text-center">加载中...</p>
                    </div>
                </div>
            </div>
            <div class="col-lg-6 mb-4">
                <div class="card shadow-sm">
                    <div class="card-header">
                        <i class="bi bi-bar-chart-fill me-1"></i>
                        预约状态概览
                    </div>
                    <div class="card-body" id="reservation-status-chart-container" style="min-height: 200px;">
                        <p class="text-center">加载中...</p>
                    </div>
                </div>
            </div>
        </div>
        `;
}

