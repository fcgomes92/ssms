import React from 'react';

import PropTypes from 'prop-types';

import classNames from 'classnames';

class SectionComponent extends React.Component {
    static propTypes = {
        className: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
    };

    static defaultProps = {
        classNames: ""
    };

    state = {
        section: null,
    };


    handleSectionRef = (ref) => {
        if (ref) {
            this.setState({section: ref});
        }
    };

    render() {
        const {children, id, className} = this.props;

        const cls = {
            section: classNames('full-height-page', className),
        };

        return (
            <section className={cls.section} ref={this.handleSectionRef} id={id}>
                {children}
            </section>
        )
    }
}

export default SectionComponent;
