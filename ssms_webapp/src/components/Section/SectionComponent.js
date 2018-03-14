import React from 'react';

class SectionComponent extends React.Component {
    static propTypes = {};

    state = {
        section: null,
    };


    handleSectionRef = (ref) => {
        if (ref) {
            this.setState({section: ref});
        }
    };

    render() {
        const {children, id} = this.props;

        const cls = {
            section: 'full-height-page',
        };

        return (
            <section className={cls.section} ref={this.handleSectionRef} id={id}>
                {children}
            </section>
        )
    }
}

export default SectionComponent;
