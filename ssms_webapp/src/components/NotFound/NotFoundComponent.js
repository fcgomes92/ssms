import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {Link} from 'react-router-dom';

import {translate} from 'react-i18next';

import '../../assets/scss/NotFound.css';
import NavbarComponent from '../Navbar/NavbarComponent';
import SimplePageMessageComponent from "../SimplePageMessage/SimplePageMessageComponent";
import BikeMountainIcon from "../svg/BikeMountainIcon";
import {URLS} from "../../routes";

class NotFoundComponent extends Component {
    static propTypes = {
        t: PropTypes.func,
        i18n: PropTypes.object,
    };

    componentDidMount() {
        const {t} = this.props;
        document.title = t('pageTitle', {page: t('contactThanksPageTitle')});
        window.scrollTo(0, 0);
    }

    render() {
        const {t} = this.props;

        const cls = {
            pageMessage: 'full-height-page not-found',
            pageMessageBg: 'not-found__bg',
            pageMessageText: 'not-found__text',
            title: 'not-found__title',
            titleText: 'not-found__title__text',
            subtitle: 'not-found__subtitle',
            subtitleText: 'not-found__subtitle__text',
            ctaLink: 'link--button--green-500 link',
        };

        return (
            <main>
                <NavbarComponent/>
                <div className={cls.pageMessage}>
                    <BikeMountainIcon className={cls.pageMessageBg}/>
                    <SimplePageMessageComponent
                        className={cls.pageMessageText}
                        title={
                            <div className={cls.title}>
                                <span className={cls.titleText}>{t('notFoundTitle')}</span>
                            </div>
                        }
                        subtitle={
                            <div className={cls.subtitle}>
                                <span className={cls.subtitleText}>{t('notFoundSubtitle')}</span>
                            </div>
                        }
                        texts={[
                            <Link key={`__not-found-cta`} className={cls.ctaLink} to={URLS.base()}>{t('notFoundCta')}</Link>
                        ]}
                    />
                </div>
            </main>
        )
    }
}

export default translate('translations')(NotFoundComponent);