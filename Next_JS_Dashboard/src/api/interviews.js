import client from './client';

export const getInterviews = async (params = {}) => {
    const { limit = 50, skip = 0 } = params;
    const response = await client.get('/interviews', {
        params: { limit, skip },
    });
    return response.data;
};

export const getInterview = async (id) => {
    const response = await client.get(`/interviews/${id}`);
    return response.data;
};

export const getEvaluation = async (id) => {
    const response = await client.get(`/interviews/${id}/evaluation`);
    return response.data;
};

export const getCandidateInterviews = async (candidateId) => {
    const response = await client.get(`/interviews/candidate/${candidateId}`);
    return response.data;
};

export const submitFeedback = async (feedbackData) => {
    const response = await client.post('/interviews/submit', feedbackData);
    return response.data;
};

export const scheduleInterview = async (scheduleData) => {
    const response = await client.post('/interviews/schedule', scheduleData);
    return response.data;
};

export const generateRanking = async (roleId) => {
    const response = await client.post(`/interviews/role/${roleId}/generate-ranking`);
    return response.data;
};

export const makeFinalDecision = async (roleId, selections, waitlist = 0) => {
    const response = await client.post(`/interviews/role/${roleId}/final-decision?selections=${selections}&waitlist=${waitlist}`);
    return response.data;
};

export const syncVoiceCall = async (callId) => {
    const response = await client.get(`/interviews/voice-sync/${callId}`);
    return response.data;
};
