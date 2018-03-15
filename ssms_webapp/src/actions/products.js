import 'whatwg-fetch';
import {getAuthHeader, URL} from "./auth";

const getProducts = async () => {
    try {
        let response = await fetch(`${URL}/products/`, {
            method: 'GET',
            headers: {
                'Authorization': getAuthHeader()
            }
        });
        return await response.json();
    } catch (e) {
        console.error(e);
        return e;
    }
};

const createProduct = async (data) => {
    try {
        let response = await fetch(`${URL}/products/`, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Authorization': getAuthHeader()
            }
        });
        return await response.json();
    } catch (e) {
        console.error(e);
        return e;
    }
};

export {getProducts, createProduct};