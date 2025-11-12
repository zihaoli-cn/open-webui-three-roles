<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let summary = {
		total_operations: 0,
		operations_by_action: {} as Record<string, number>,
		operations_by_user_role: {} as Record<string, number>,
		operations_by_resource_type: {} as Record<string, number>,
		failed_operations: 0,
		unique_users: 0
	};

	let loginSummary = {
		total_logins: 0,
		successful_logins: 0,
		failed_logins: 0,
		logins_by_type: {} as Record<string, number>,
		unique_users: 0
	};

	let loading = false;

	async function loadSummary() {
		loading = true;
		try {
			// Get last 7 days
			const endTime = Math.floor(Date.now() / 1000);
			const startTime = endTime - 7 * 24 * 60 * 60;

			// Load audit summary
			const auditResponse = await fetch(
				`/api/v1/audit/summary?start_time=${startTime}&end_time=${endTime}`
			);
			if (auditResponse.ok) {
				summary = await auditResponse.json();
			}

			// Load login summary
			const loginResponse = await fetch(
				`/api/v1/audit/logins/summary?start_time=${startTime}&end_time=${endTime}`
			);
			if (loginResponse.ok) {
				loginSummary = await loginResponse.json();
			}
		} catch (error) {
			console.error('Error loading summary:', error);
		} finally {
			loading = false;
		}
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

	onMount(() => {
		loadSummary();
	});
</script>

<div class="p-6">
	<h1 class="text-3xl font-bold mb-6">安全审计控制台</h1>

	{#if loading}
		<div class="flex justify-center items-center h-64">
			<div class="text-gray-500">加载中...</div>
		</div>
	{:else}
		<!-- Quick Stats -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">总操作数（7天）</div>
				<div class="text-3xl font-bold">{summary.total_operations}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">失败操作</div>
				<div class="text-3xl font-bold text-red-600">{summary.failed_operations}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">总登录次数（7天）</div>
				<div class="text-3xl font-bold">{loginSummary.total_logins}</div>
			</div>
			<div class="bg-white p-6 rounded-lg shadow">
				<div class="text-sm text-gray-600 mb-2">登录失败次数</div>
				<div class="text-3xl font-bold text-red-600">{loginSummary.failed_logins}</div>
			</div>
		</div>

		<!-- Quick Links -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
			<button
				on:click={() => goto('/audit-admin/audit-logs')}
				class="bg-blue-600 text-white p-6 rounded-lg shadow hover:bg-blue-700 text-left"
			>
				<h2 class="text-xl font-bold mb-2">审计日志查询</h2>
				<p class="text-blue-100">查看所有用户和管理员的操作记录</p>
			</button>
			<button
				on:click={() => goto('/audit-admin/login-logs')}
				class="bg-green-600 text-white p-6 rounded-lg shadow hover:bg-green-700 text-left"
			>
				<h2 class="text-xl font-bold mb-2">登录日志查询</h2>
				<p class="text-green-100">查看所有登录尝试记录</p>
			</button>
		</div>

		<!-- Summary Tables -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Operations by Action -->
			<div class="bg-white p-6 rounded-lg shadow">
				<h3 class="text-lg font-bold mb-4">按操作类型统计</h3>
				<table class="w-full">
					<thead>
						<tr class="border-b">
							<th class="text-left py-2">操作类型</th>
							<th class="text-right py-2">次数</th>
						</tr>
					</thead>
					<tbody>
						{#each Object.entries(summary.operations_by_action) as [action, count]}
							<tr class="border-b">
								<td class="py-2">{getActionLabel(action)}</td>
								<td class="text-right py-2">{count}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Operations by User Role -->
			<div class="bg-white p-6 rounded-lg shadow">
				<h3 class="text-lg font-bold mb-4">按用户角色统计</h3>
				<table class="w-full">
					<thead>
						<tr class="border-b">
							<th class="text-left py-2">用户角色</th>
							<th class="text-right py-2">操作次数</th>
						</tr>
					</thead>
					<tbody>
						{#each Object.entries(summary.operations_by_user_role) as [role, count]}
							<tr class="border-b">
								<td class="py-2">{getRoleLabel(role)}</td>
								<td class="text-right py-2">{count}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Logins by Type -->
			<div class="bg-white p-6 rounded-lg shadow">
				<h3 class="text-lg font-bold mb-4">按登录方式统计</h3>
				<table class="w-full">
					<thead>
						<tr class="border-b">
							<th class="text-left py-2">登录方式</th>
							<th class="text-right py-2">次数</th>
						</tr>
					</thead>
					<tbody>
						{#each Object.entries(loginSummary.logins_by_type) as [type, count]}
							<tr class="border-b">
								<td class="py-2">{getLoginTypeLabel(type)}</td>
								<td class="text-right py-2">{count}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Operations by Resource Type -->
			<div class="bg-white p-6 rounded-lg shadow">
				<h3 class="text-lg font-bold mb-4">按资源类型统计</h3>
				<table class="w-full">
					<thead>
						<tr class="border-b">
							<th class="text-left py-2">资源类型</th>
							<th class="text-right py-2">操作次数</th>
						</tr>
					</thead>
					<tbody>
						{#each Object.entries(summary.operations_by_resource_type).slice(0, 10) as [type, count]}
							<tr class="border-b">
								<td class="py-2">{type}</td>
								<td class="text-right py-2">{count}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>
