import React from 'react';
import {render} from 'react-dom';

import {I18nextProvider} from 'react-i18next';

import i18n from './i18n';
import './settings/settings';
import App from './components/App/AppComponent';

render(
    <I18nextProvider i18n={i18n}><App/></I18nextProvider>,
    document.getElementById('root'),
    () => {
        let initialLoading = document.getElementById("initialLoading");
        initialLoading.style.opacity = 0;
        setTimeout(() => {
            initialLoading.style.display = 'none';
        }, 250);

    });
