import api from '../api/axios'; // Assuming standard axios setup

export const enhanceEventImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/v1/image/enhance', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Expecting an image blob back
    });

    return response.data;
};
