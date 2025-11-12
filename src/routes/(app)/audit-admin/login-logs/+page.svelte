<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	interface LoginLog {
		id: string;
		user_id: string | null;
		user_email: string;
		login_type: string;
		status: string;
		failure_reason: string | null;
		ip_address: string;
		user_agent: string | null;
		timestamp: number;
	}

	let logs: LoginLog[] = [];
	let totalCount = 0;
	let loading = false;

	// Filters
	let filters = {
		user_email: '',
		login_type: '',
		status: '',
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

			if (filters.user_email) params.append('user_email', filters.user_email);
			if (filters.login_type) params.append('login_type', filters.login_type);
			if (filters.status) params.append('status', filters.status);
			if (filters.start_time) params.append('start_time', String(filters.start_time));
			if (filters.end_time) params.append('end_time', String(filters.end_time));
			if (filters.ip_address) params.append('ip_address', filters.ip_address);

			const response = await fetch(`/api/v1/audit/logins?${params}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				logs = await response.json();
			} else {
				toast.error('Failed to load login logs');
			}

			// Load count
			const countResponse = await fetch(`/api/v1/audit/logins/count?${params}`, {
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
			console.error('Error loading login logs:', error);
			toast.error('Error loading login logs');
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

	function getLoginTypeLabel(type: string): string {
		const typeMap: { [key: string]: string } = {
			password: '密码登录',
			oauth: 'OAuth登录',
			ldap: 'LDAP登录',
			api_key: 'API密钥',
			trusted_header: '信任头部',
			no_auth: '无认证'
		};
		return typeMap[type] || type;
	}

	function getStatusColor(status: string): string {
		return status === 'success' ? 'text-green-600' : 'text-red-600';
	}

	function getStatusLabel(status: string): string {
		return status === 'success' ? '成功' : '失败';
	}

	function resetFilters() {
		filters = {
			user_email: '',
			login_type: '',
			status: '',
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
		if (currentPage * pageSize < totalCount) {
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
		<h1 class="text-2xl font-bold mb-4">登录日志查询</h1>

		<!-- Filters -->
		<div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-4">
			<input
				type="text"
				bind:value={filters.user_email}
				placeholder="用户邮箱"
				class="px-3 py-2 border rounded-lg"
			/>
			<select bind:value={filters.login_type} class="px-3 py-2 border rounded-lg">
				<option value="">所有登录方式</option>
				<option value="password">密码登录</option>
				<option value="oauth">OAuth登录</option>
				<option value="ldap">LDAP登录</option>
				<option value="api_key">API密钥</option>
			</select>
			<select bind:value={filters.status} class="px-3 py-2 border rounded-lg">
				<option value="">所有状态</option>
				<option value="success">成功</option>
				<option value="failed">失败</option>
			</select>
			<input
				type="text"
				bind:value={filters.ip_address}
				placeholder="IP地址"
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
				<div class="text-gray-500">没有找到登录日志</div>
			</div>
		{:else}
			<table class="w-full border-collapse">
				<thead>
					<tr class="bg-gray-100">
						<th class="px-4 py-2 text-left">时间</th>
						<th class="px-4 py-2 text-left">用户邮箱</th>
						<th class="px-4 py-2 text-left">登录方式</th>
						<th class="px-4 py-2 text-left">状态</th>
						<th class="px-4 py-2 text-left">失败原因</th>
						<th class="px-4 py-2 text-left">IP地址</th>
					</tr>
				</thead>
				<tbody>
					{#each logs as log}
						<tr class="border-b hover:bg-gray-50">
							<td class="px-4 py-2 text-sm">{formatTimestamp(log.timestamp)}</td>
							<td class="px-4 py-2 text-sm">{log.user_email}</td>
							<td class="px-4 py-2 text-sm">{getLoginTypeLabel(log.login_type)}</td>
							<td class="px-4 py-2 text-sm {getStatusColor(log.status)}">
								{getStatusLabel(log.status)}
							</td>
							<td class="px-4 py-2 text-sm text-red-600">
								{log.failure_reason || '-'}
							</td>
							<td class="px-4 py-2 text-sm">{log.ip_address}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>

	<!-- Pagination -->
	<div class="p-4 border-t flex justify-between items-center">
		<div class="text-sm text-gray-600">共 {totalCount} 条记录，第 {currentPage} 页</div>
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
