import {disableLog} from '../util';

export const VERSION = '1.1.0';
export const DOMAIN = 'https://pousadacaminhodosventos.com';
export const DEBUG = process.env.NODE_ENV === 'development';

export const CMS_URL = 'https://cms.pousadacaminhodosventos.com/wp-json/wp/v2/media?search=site-&per_page=100';

disableLog();
