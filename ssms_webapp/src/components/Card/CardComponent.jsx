import React from 'react';

import PropTypes from 'prop-types';

import classNames from 'classnames';

import '../../assets/scss/Card.css';

class CardTitleComponent extends React.Component {
    static propTypes = {
        primaryText: PropTypes.string,
        secondaryText: PropTypes.string,
    };

    render() {
        const {primaryText, secondaryText} = this.props;
        const cls = {
            cardTitleContainer: 'card__title__container',
            cardTitlePrimaryText: 'card__title__primary-text',
            cardTitlePrimaryTextText: 'card__title__primary-text__text',
            cardTitleSecondaryText: 'card__title__secondary-text',
            cardTitleSecondaryTextText: 'card__title__secondary-text__text',
        };

        return (
            <div className={cls.cardTitleContainer}>
                <div className={cls.cardTitlePrimaryText}>
                    <span className={cls.cardTitlePrimaryTextText}>{primaryText}</span>
                </div>
                <div className={cls.cardTitleSecondaryText}>
                    <span className={cls.cardTitleSecondaryTextText}>{secondaryText}</span>
                </div>
            </div>
        )
    }
}

class CardActionsComponent extends React.Component {
    render() {
        const {children} = this.props;
        const cls = {
            actions: 'card__actions',
        };
        return (<div className={cls.actions}>{children}</div>)
    }
}

class CardMediaComponent extends React.Component {
    render() {
        const {srcImg} = this.props;
        const cls = {
            cardMedia: 'card__media',
        };
        return (<div className={cls.cardMedia} style={{backgroundImage: `url(${srcImg})`}}/>)
    }
}

class CardContentComponent extends React.Component {
    render() {
        const {children} = this.props;
        const cls = {
            cardContent: 'card__content',
        };
        return (<div className={cls.cardContent}>{children}</div>)
    }
}

class CardComponent extends React.Component {
    static propTypes = {
        zIndex: PropTypes.number,
    };

    render() {
        const {children, zIndex} = this.props;
        const cls = {
            card: classNames('card', {
                [`card--shadow-${zIndex}`]: true,
            }),
        };
        return (<div className={cls.card}>{children}</div>)
    }
}

export {CardComponent, CardActionsComponent, CardContentComponent, CardMediaComponent, CardTitleComponent};