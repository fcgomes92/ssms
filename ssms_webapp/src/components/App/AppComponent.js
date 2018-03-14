import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {
    Router,
    Switch,
    Route,
} from 'react-router-dom';
import createBrowserHistory from 'history/createBrowserHistory';

import {translate} from 'react-i18next';

import {ROUTES} from '../../routes';
import {DEBUG} from '../../settings/settings';
import '../../assets/scss/App.css';

const customHistory = createBrowserHistory();

// send page view to GA on each history change
customHistory.listen((location, action) => {
    if (!DEBUG) {
        try {
            //eslint-disable-next-line
            window.ga('create', 'UA-98009377-1', 'auto');
            //eslint-disable-next-line
            window.ga('send', 'pageview', location.pathname);
        } catch (e) {

        }
    }
});


class AppComponent extends Component {
    static propTypes = {
        t: PropTypes.func,
        i18n: PropTypes.object,
    };

    componentDidMount() {
        const {t} = this.props;
        document.title = t('homePageTitle');
    }

    render() {
        return (
            <Router history={customHistory}>
                <Switch>
                    {
                        ROUTES.map(route => {
                            return <Route exact={route.exact}
                                          path={route.path}
                                          component={route.component}
                                          key={`__key_${route.name}`}
                            />
                        })
                    }
                </Switch>
            </Router>
        )
    }
}

export default translate('translations')(AppComponent);
