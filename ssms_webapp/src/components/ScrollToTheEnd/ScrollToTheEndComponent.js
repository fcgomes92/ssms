import React, {Component} from 'react';
import PropTypes from 'prop-types';

import '../../assets/scss/BannerHeader.css';

class ScrollToTheEndComponent extends Component {
    static propTypes = {
        element: PropTypes.object,
    };

    animationTime = 50;

    handleScrollToAnimation = (step, currentScrollHeight, maxScrollHeight) => {
        if (currentScrollHeight < maxScrollHeight) {
            window.scrollTo(0, currentScrollHeight + step);
            setTimeout(() => {
                this.handleScrollToAnimation(step, currentScrollHeight + step, maxScrollHeight);
            }, step);
        }
    };


    handleScrollToSectionEnd = () => {
        const {element} = this.props;
        const html = document.getElementsByTagName("html")[0];
        if (element) {
            let scrollPos = window.scrollY || window.scollTop || html.scrollTop;
            let elementRect = element.getBoundingClientRect();
            let maxScrollHeight = elementRect.top + scrollPos + element.scrollHeight;
            let step = maxScrollHeight / this.animationTime;

            this.handleScrollToAnimation(step, scrollPos, maxScrollHeight);
        }
    };


    render() {
        const {children} = this.props;
        return React.cloneElement(
            children,
            Object.assign({}, children.props, {onClick: this.handleScrollToSectionEnd}),
        )
    }
}

export default ScrollToTheEndComponent;
