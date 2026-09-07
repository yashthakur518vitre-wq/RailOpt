import client from './client';

export const generatePlan = async (horizon: string) => {
  const res = await client.post('/planning/generate?horizon=' + horizon);
  return res.data.data;
};

export const getPlan = async (planId: string) => {
  const res = await client.get('/planning/' + planId);
  return res.data.data;
};

export const approvePlan = async (planId: string) => {
  const res = await client.post('/planning/' + planId + '/approve');
  return res.data.data;
};

export const getPlans = async () => {
  const res = await client.get('/planning');
  return res.data.data;
};
