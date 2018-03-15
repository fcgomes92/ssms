import 'whatwg-fetch';

const VERSION = `v1`;
const URL = `http://localhost:8000/${VERSION}`;

const getAuthHeader = (email = null, password = null) => {
    let token = localStorage.getItem(`token`);
    if (token) {
        return `Token ${token}`
    } else {
        return `Basic ${btoa(`${email}:${password}`)}`
    }
};

const login = async (email, password) => {
    try {
        let response = await fetch(`${URL}/users/auth/`, {
            method: 'POST',
            headers: {
                'Authorization': getAuthHeader(email, password)
            }
        });
        return await response.json();
    } catch (e) {
        console.error(e);
        return e;
    }

};

export {login, getAuthHeader, URL};