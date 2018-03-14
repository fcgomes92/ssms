import React from 'react';

import PropTypes from 'prop-types';

import '../../assets/scss/List.css';

class ListComponent extends React.Component {
    render() {
        const cls = {
            list: 'list',
        };

        return (
            <ul className={cls.list}>{this.props.children}</ul>
        )
    }
}

class ListItemComponent extends React.Component {
    static propTypes = {
        href: PropTypes.string,
        target: PropTypes.string,
        primaryText: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
        leftIcon: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
        onClick: PropTypes.func,
    };

    static defaultProps = {
        href: null,
        target: '_self',
    };

    renderContent() {
        const {href, target, leftIcon, onClick, primaryText} = this.props;
        const cls = {
            listItemContent: 'list__item__content',
            listItemLeftIcon: 'list__item__left-icon',
            listItemText: 'list__item__text',
        };

        let rel = target === '_blank' ? 'noopener noreferrer' : '';

        if (href) {
            return (
                <a href={href} rel={rel} target={target} className={cls.listItemContent}>
                    {leftIcon ? <span className={cls.listItemLeftIcon}>{leftIcon}</span> : null}
                    <span className={cls.listItemText}>{primaryText}</span>
                </a>)
        } else {
            return (
                <div onClick={onClick} className={cls.listItemContent}>
                    {leftIcon ? <span className={cls.listItemLeftIcon}>{leftIcon}</span> : null}
                    <span className={cls.listItemText}>{primaryText}</span>
                </div>
            );
        }
    }

    render() {
        const cls = {
            listItem: 'list__item',
        };
        return (
            <li className={cls.listItem}>{this.renderContent()}</li>
        )
    }
}

export {ListComponent, ListItemComponent};