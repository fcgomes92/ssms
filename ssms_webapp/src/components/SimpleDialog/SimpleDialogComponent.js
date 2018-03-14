import React from 'react';
import PropTypes from 'prop-types';

import classNames from 'classnames';

import '../../assets/scss/SimpleDialog.css';

class SimpleDialogComponent extends React.Component {
    static propTypes = {
        open: PropTypes.bool,
        onRequestClose: PropTypes.func,
    };

    static defaultProps = {
        open: false,
    };

    containerRef = null;
    handleContainerOnKeyDownListener = (event) => {
        if (event.keyCode === 27) {
            this.handleOnRequestClose();
        }
    };
    handleToggleKeyListener = (open) => {
        if (open) {
            document.addEventListener('keydown', this.handleContainerOnKeyDownListener);
        } else {
            document.removeEventListener('keydown', this.handleContainerOnKeyDownListener);
        }
    };
    handleContainerRef = (container) => {
        if (container) {
            this.containerRef = container;
        }
    };

    handleOnRequestClose = () => {
        const {onRequestClose} = this.props;
        if (onRequestClose) {
            onRequestClose();
        }
    };

    componentWillReceiveProps(newProps) {
        const {open} = this.props;
        if (open !== newProps.open)
            this.handleToggleKeyListener(newProps.open);
    }

    renderContent() {
        return null;
    }

    render() {
        const {open} = this.props;

        const cls = {
            simpleDialog: classNames('simple-dialog', {'show': open}),
            simpleDialogOverlay: 'simple-dialog__overlay',
            simpleDialogContent: 'simple-dialog__content',
        };

        return (
            <div className={cls.simpleDialog}
                 ref={this.handleContainerRef}>
                <div className={cls.simpleDialogOverlay}
                     onClick={this.handleOnRequestClose}/>
                <div className={cls.simpleDialogContent}>
                    {this.renderContent()}
                </div>
            </div>
        )
    }
}

export default SimpleDialogComponent;
