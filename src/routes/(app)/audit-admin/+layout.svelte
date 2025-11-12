<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { get } from 'svelte/store';

	onMount(() => {
		const currentUser = get(user);
		// Only audit_admin can access this section
		if (currentUser?.role !== 'audit_admin') {
			goto('/');
		}
	});
</script>

<div class="flex flex-col h-full">
	<div class="border-b bg-gray-50 dark:bg-gray-900">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<div class="flex">
					<div class="flex-shrink-0 flex items-center">
						<h1 class="text-xl font-bold">安全审计管理</h1>
					</div>
					<nav class="ml-6 flex space-x-4 items-center">
						<a
							href="/audit-admin"
							class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-800"
						>
							仪表盘
						</a>
						<a
							href="/audit-admin/audit-logs"
							class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-800"
						>
							审计日志
						</a>
						<a
							href="/audit-admin/login-logs"
							class="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-800"
						>
							登录日志
						</a>
					</nav>
				</div>
			</div>
		</div>
	</div>

	<div class="flex-1 overflow-auto">
		<slot />
	</div>
</div>
