import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {translate} from 'react-i18next';

import {NavLink} from 'react-router-dom';

import classNames from 'classnames';

import {URLS} from '../../routes';
import '../../assets/scss/Navbar.css';

class NavbarComponent extends Component {
    static propTypes = {
        t: PropTypes.func,
        i18n: PropTypes.object,
    };

    state = {
        leftNavOpen: false,
    };

    handleToggleLeftNav = () => {
        const {leftNavOpen} = this.state;
        this.setState({leftNavOpen: !leftNavOpen})
    };

    render() {
        const {t} = this.props;
        const {leftNavOpen} = this.state;

        const cls = {
            smallNav: 'small-navbar navbar--shadow',
            smallNavLogo: 'small-navbar__logo responsive-width',
            smallNavMenuBtn: classNames('menu-btn flat-button flat-button--white-text', {'menu-btn--hide': leftNavOpen}),
            menuBtn: 'menu-btn flat-button flat-button--white-text',
            nav: classNames('navbar navbar--shadow', {'navbar--show': leftNavOpen}),
            navBackground: classNames('navbar-background', {'navbar-background--show': leftNavOpen}),
            navLogo: 'navbar__logo responsive-width',
            navSocial: 'navbar__social-links',
            navSocialLink: 'navbar__social-links__link',
            navLinks: 'navbar__links navbar__links--show-only-large',
            navLink: 'navbar__links__link',
            navLinkText: 'navbar__links__link__text',
            navLinkSelected: 'navbar__links__link--selected',
        };

        return (
            <nav>
                <div className={cls.smallNav}>
                    <button className={cls.smallNavMenuBtn}
                            onClick={this.handleToggleLeftNav}>
                        <i className="material-icons">{leftNavOpen ? `close` : `menu`}</i>
                    </button>
                </div>
                <div className={cls.navBackground} onClick={this.handleToggleLeftNav}>
                    <button className={cls.menuBtn}
                            onClick={this.handleToggleLeftNav}>
                        <i className="material-icons">{leftNavOpen ? `close` : `menu`}</i>
                    </button>
                </div>
                <div className={cls.nav}>
                    <div className={cls.navLinks}>
                        <NavLink exact className={cls.navLink} activeClassName={cls.navLinkSelected} to={URLS.base()}>
                            <span className={cls.navLinkText}>{t('navbarHome')}</span>
                        </NavLink>
                    </div>
                </div>
            </nav>
        )
    }
}

export default translate('translations')(NavbarComponent);
