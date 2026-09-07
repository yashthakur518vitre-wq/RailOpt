import client from './client';

export const getMaintenanceTasks = async () => {
  const res = await client.get('/maintenance');
  return res.data.data;
};
