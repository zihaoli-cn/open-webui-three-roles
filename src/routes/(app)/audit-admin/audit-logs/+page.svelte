<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	interface AuditLog {
		id: string;
		user_id: string;
		user_name: string;
		user_email: string;
		user_role: string;
		action: string;
		resource_type: string;
		resource_id: string | null;
		method: string;
		endpoint: string;
		request_body: string | null;
		response_status: number;
		response_body: string | null;
		ip_address: string;
		user_agent: string | null;
		timestamp: number;
	}

	let logs: AuditLog[] = [];
	let totalCount = 0;
	let loading = false;
	let selectedLog: AuditLog | null = null;
	let showDetailModal = false;

	// Filters
	let filters = {
		user_id: '',
		user_role: '',
		action: '',
		resource_type: '',
		start_time: null as number | null,
		end_time: null as number | null,
		ip_address: ''
	};

	// Pagination
	let currentPage = 1;
	let pageSize = 50;

	async function loadLogs() {
		loading = true;
		try {
			const params = new URLSearchParams();
			params.append('skip', String((currentPage - 1) * pageSize));
			params.append('limit', String(pageSize));

			if (filters.user_id) params.append('user_id', filters.user_id);
			if (filters.user_role) params.append('user_role', filters.user_role);
			if (filters.action) params.append('action', filters.action);
			if (filters.resource_type) params.append('resource_type', filters.resource_type);
			if (filters.start_time) params.append('start_time', String(filters.start_time));
			if (filters.end_time) params.append('end_time', String(filters.end_time));
			if (filters.ip_address) params.append('ip_address', filters.ip_address);

			const response = await fetch(`/api/v1/audit/logs?${params}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				logs = await response.json();
			} else {
				toast.error('Failed to load audit logs');
			}

			// Load count
			const countResponse = await fetch(`/api/v1/audit/logs/count?${params}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (countResponse.ok) {
				const countData = await countResponse.json();
				totalCount = countData.count;
			}
		} catch (error) {
			console.error('Error loading audit logs:', error);
			toast.error('Error loading audit logs');
		} finally {
			loading = false;
		}
	}

	function formatTimestamp(timestamp: number): string {
		return new Date(timestamp * 1000).toLocaleString('zh-CN', {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}

	function getRoleLabel(role: string): string {
		const roleMap: { [key: string]: string } = {
			system_admin: '系统管理员',
			auth_admin: '授权管理员',
			audit_admin: '安全审计员',
			admin: '管理员',
			user: '普通用户',
			pending: '待审核'
		};
		return roleMap[role] || role;
	}

	function getActionLabel(action: string): string {
		const actionMap: { [key: string]: string } = {
			CREATE: '创建',
			UPDATE: '更新',
			DELETE: '删除',
			READ: '读取',
			LOGIN: '登录',
			LOGOUT: '登出'
		};
		return actionMap[action] || action;
	}

	function getStatusColor(status: number): string {
		if (status >= 200 && status < 300) return 'text-green-600';
		if (status >= 400 && status < 500) return 'text-yellow-600';
		if (status >= 500) return 'text-red-600';
		return 'text-gray-600';
	}

	function viewDetails(log: AuditLog) {
		selectedLog = log;
		showDetailModal = true;
	}

	function closeDetailModal() {
		showDetailModal = false;
		selectedLog = null;
	}

	function resetFilters() {
		filters = {
			user_id: '',
			user_role: '',
			action: '',
			resource_type: '',
			start_time: null,
			end_time: null,
			ip_address: ''
		};
		currentPage = 1;
		loadLogs();
	}

	function handleSearch() {
		currentPage = 1;
		loadLogs();
	}

	function nextPage() {
		if ((currentPage * pageSize) < totalCount) {
			currentPage++;
			loadLogs();
		}
	}

	function prevPage() {
		if (currentPage > 1) {
			currentPage--;
			loadLogs();
		}
	}

	onMount(() => {
		loadLogs();
	});
</script>

<div class="flex flex-col h-full">
	<div class="p-6 border-b">
		<h1 class="text-2xl font-bold mb-4">审计日志查询</h1>

		<!-- Filters -->
		<div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-4">
			<input
				type="text"
				bind:value={filters.user_id}
				placeholder="用户ID"
				class="px-3 py-2 border rounded-lg"
			/>
			<select bind:value={filters.user_role} class="px-3 py-2 border rounded-lg">
				<option value="">所有角色</option>
				<option value="system_admin">系统管理员</option>
				<option value="auth_admin">授权管理员</option>
				<option value="audit_admin">安全审计员</option>
				<option value="admin">管理员</option>
				<option value="user">普通用户</option>
			</select>
			<select bind:value={filters.action} class="px-3 py-2 border rounded-lg">
				<option value="">所有操作</option>
				<option value="CREATE">创建</option>
				<option value="UPDATE">更新</option>
				<option value="DELETE">删除</option>
				<option value="READ">读取</option>
				<option value="LOGIN">登录</option>
			</select>
			<input
				type="text"
				bind:value={filters.resource_type}
				placeholder="资源类型"
				class="px-3 py-2 border rounded-lg"
			/>
		</div>

		<div class="flex gap-2">
			<button
				on:click={handleSearch}
				class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
			>
				查询
			</button>
			<button
				on:click={resetFilters}
				class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
			>
				重置
			</button>
		</div>
	</div>

	<!-- Table -->
	<div class="flex-1 overflow-auto p-6">
		{#if loading}
			<div class="flex justify-center items-center h-full">
				<div class="text-gray-500">加载中...</div>
			</div>
		{:else if logs.length === 0}
			<div class="flex justify-center items-center h-full">
				<div class="text-gray-500">没有找到审计日志</div>
			</div>
		{:else}
			<table class="w-full border-collapse">
				<thead>
					<tr class="bg-gray-100">
						<th class="px-4 py-2 text-left">时间</th>
						<th class="px-4 py-2 text-left">用户</th>
						<th class="px-4 py-2 text-left">角色</th>
						<th class="px-4 py-2 text-left">操作</th>
						<th class="px-4 py-2 text-left">资源类型</th>
						<th class="px-4 py-2 text-left">端点</th>
						<th class="px-4 py-2 text-left">状态</th>
						<th class="px-4 py-2 text-left">IP地址</th>
						<th class="px-4 py-2 text-left">操作</th>
					</tr>
				</thead>
				<tbody>
					{#each logs as log}
						<tr class="border-b hover:bg-gray-50">
							<td class="px-4 py-2 text-sm">{formatTimestamp(log.timestamp)}</td>
							<td class="px-4 py-2 text-sm">{log.user_name}</td>
							<td class="px-4 py-2 text-sm">{getRoleLabel(log.user_role)}</td>
							<td class="px-4 py-2 text-sm">{getActionLabel(log.action)}</td>
							<td class="px-4 py-2 text-sm">{log.resource_type}</td>
							<td class="px-4 py-2 text-sm font-mono text-xs">{log.endpoint}</td>
							<td class="px-4 py-2 text-sm {getStatusColor(log.response_status)}">
								{log.response_status}
							</td>
							<td class="px-4 py-2 text-sm">{log.ip_address}</td>
							<td class="px-4 py-2 text-sm">
								<button
									on:click={() => viewDetails(log)}
									class="text-blue-600 hover:underline"
								>
									详情
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>

	<!-- Pagination -->
	<div class="p-4 border-t flex justify-between items-center">
		<div class="text-sm text-gray-600">
			共 {totalCount} 条记录，第 {currentPage} 页
		</div>
		<div class="flex gap-2">
			<button
				on:click={prevPage}
				disabled={currentPage === 1}
				class="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
			>
				上一页
			</button>
			<button
				on:click={nextPage}
				disabled={currentPage * pageSize >= totalCount}
				class="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
			>
				下一页
			</button>
		</div>
	</div>
</div>

<!-- Detail Modal -->
{#if showDetailModal && selectedLog}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
		<div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
			<div class="p-6 border-b flex justify-between items-center">
				<h2 class="text-xl font-bold">审计日志详情</h2>
				<button on:click={closeDetailModal} class="text-gray-500 hover:text-gray-700">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
			<div class="p-6 space-y-4">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="font-semibold">时间:</label>
						<p>{formatTimestamp(selectedLog.timestamp)}</p>
					</div>
					<div>
						<label class="font-semibold">用户:</label>
						<p>{selectedLog.user_name} ({selectedLog.user_email})</p>
					</div>
					<div>
						<label class="font-semibold">角色:</label>
						<p>{getRoleLabel(selectedLog.user_role)}</p>
					</div>
					<div>
						<label class="font-semibold">操作:</label>
						<p>{getActionLabel(selectedLog.action)}</p>
					</div>
					<div>
						<label class="font-semibold">资源类型:</label>
						<p>{selectedLog.resource_type}</p>
					</div>
					<div>
						<label class="font-semibold">资源ID:</label>
						<p>{selectedLog.resource_id || 'N/A'}</p>
					</div>
					<div>
						<label class="font-semibold">HTTP方法:</label>
						<p>{selectedLog.method}</p>
					</div>
					<div>
						<label class="font-semibold">响应状态:</label>
						<p class={getStatusColor(selectedLog.response_status)}>
							{selectedLog.response_status}
						</p>
					</div>
					<div>
						<label class="font-semibold">IP地址:</label>
						<p>{selectedLog.ip_address}</p>
					</div>
					<div class="col-span-2">
						<label class="font-semibold">端点:</label>
						<p class="font-mono text-sm">{selectedLog.endpoint}</p>
					</div>
				</div>

				{#if selectedLog.request_body}
					<div>
						<label class="font-semibold">请求体:</label>
						<pre
							class="mt-2 p-4 bg-gray-100 rounded-lg overflow-auto max-h-48 text-sm">{selectedLog.request_body}</pre>
					</div>
				{/if}

				{#if selectedLog.response_body}
					<div>
						<label class="font-semibold">响应体:</label>
						<pre
							class="mt-2 p-4 bg-gray-100 rounded-lg overflow-auto max-h-48 text-sm">{selectedLog.response_body}</pre>
					</div>
				{/if}

				{#if selectedLog.user_agent}
					<div>
						<label class="font-semibold">User Agent:</label>
						<p class="text-sm text-gray-600">{selectedLog.user_agent}</p>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
