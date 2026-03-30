import client from './client';

export const getCandidates = async (params = {}) => {
    const { limit = 100, skip = 0, role_id, status, stage } = params;
    const response = await client.get('/candidates', {
        params: {
            limit,
            skip,
            ...(role_id != null && { role_id }),
            ...(status && { status }),
            ...(stage && { stage }),
        },
    });
    return response.data;
};

export const getCandidate = async (id) => {
    const response = await client.get(`/candidates/${id}`);
    return response.data;
};

export const createCandidate = async (formData) => {
    const response = await client.post('/candidates/submit', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const evaluateCandidate = async (id, roleId) => {
    const response = await client.post(`/candidates/${id}/evaluate`, { role_id: roleId });
    return response.data;
};

export const updateCandidateStage = async (id, stage) => {
    const response = await client.put(`/candidates/${id}/stage`, { stage });
    return response.data;
};

export const getCandidateScores = async (id) => {
    const response = await client.get(`/candidates/${id}/scores`);
    return response.data;
};
