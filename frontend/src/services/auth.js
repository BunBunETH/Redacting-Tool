import api from './api';

export const login = async (username, password) => {
    try {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        
        const response = await api.post('/auth/login', params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        
        if (response.data.access_token) {
            localStorage.setItem('user', JSON.stringify(response.data));
            // Set the token in the API client
            api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
        }
        
        return response.data;
    } catch (error) {
        console.error('Login error:', error);
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            if (error.response.status === 422) {
                throw new Error('Invalid username or password format');
            } else if (error.response.status === 401) {
                throw new Error('Invalid credentials');
            } else {
                throw new Error('Login failed. Please try again.');
            }
        } else if (error.request) {
            // The request was made but no response was received
            throw new Error('No response from server. Please try again.');
        } else {
            // Something happened in setting up the request that triggered an Error
            throw new Error('Error setting up request. Please try again.');
        }
    }
};

export const register = async (userData) => {
    try {
        const response = await api.post('/auth/register', userData, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Registration error:', error);
        if (error.response) {
            throw new Error(error.response.data.detail || 'Registration failed');
        } else if (error.request) {
            throw new Error('No response from server. Please try again.');
        } else {
            throw new Error('Error setting up request. Please try again.');
        }
    }
};

export const logout = () => {
    localStorage.removeItem('user');
};

export const getCurrentUser = () => {
    return JSON.parse(localStorage.getItem('user'));
}; 