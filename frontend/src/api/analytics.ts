import client from './client';

export const getDashboardSummary = async () => {
  const response = await client.get('/dashboard/summary');
  const d = response.data.data;
  const kpis = d.kpis || {};
  
  return {
    assetAvailability: (kpis['Asset Availability %'] || 0) / 100,
    maintenanceCompletion: (kpis['Maintenance Completion %'] || 0) / 100,
    criticalTasks: kpis['Critical Task Completion %'] || 0, // Not "Critical Tasks Pending", actually completion %
    activeBlocks: kpis['Number of Blocks'] || d.active_blocks?.length || 0,
    trainImpact: kpis['Train Impact Score'] || 0,
    overdueTasks: kpis['Overdue Tasks'] || 0,
    rawCriticalTasks: d.recent_tasks || [],
    rawActiveBlocks: d.active_blocks || []
  };
};

export const getDepartmentDistribution = async () => {
  const response = await client.get('/maintenance');
  const tasks = response.data.data || [];
  const dist: Record<string, number> = {};
  tasks.forEach((t: any) => {
    dist[t.department] = (dist[t.department] || 0) + 1;
  });
  return Object.keys(dist).map(k => ({ name: k, value: dist[k] }));
};
