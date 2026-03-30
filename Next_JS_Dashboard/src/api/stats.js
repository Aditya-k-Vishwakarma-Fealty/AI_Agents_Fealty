import client from './client';

export const getDashboardStats = async () => {
  const response = await client.get('/stats');
  return response.data;
};
