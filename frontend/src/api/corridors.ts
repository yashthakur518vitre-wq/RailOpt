import client from './client';

export const getCorridors = async () => {
  const res = await client.get('/corridors');
  return res.data.data;
};
