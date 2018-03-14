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
        const {children} = this.props;
        return (
            <section ref={this.handleSectionRef} id={"banner"}>
                {children}
            </section>
        )
    }
}

export default SectionComponent;
