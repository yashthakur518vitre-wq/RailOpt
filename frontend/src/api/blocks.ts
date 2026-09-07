import client from './client';

export const getBlocks = async () => {
  const res = await client.get('/blocks');
  return res.data.data;
};
