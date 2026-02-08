import client from './client';

export const getRoles = async () => {
    const response = await client.get('/roles');
    return response.data;
};

export const getRole = async (id) => {
    const response = await client.get(`/roles/${id}`);
    return response.data;
};

export const createRole = async (roleData) => {
    const response = await client.post('/roles/create', roleData);
    return response.data;
};

export const shortlistRole = async (id, threshold) => {
    const response = await client.post(`/roles/${id}/shortlist`, { threshold });
    return response.data;
};

export const getRoleCandidates = async (id) => {
    const response = await client.get(`/roles/${id}/candidates`);
    return response.data;
};

export const getRoleRankings = async (id) => {
    const response = await client.get(`/roles/${id}/rankings`);
    return response.data;
};
