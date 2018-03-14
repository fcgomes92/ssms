import React, {Component} from 'react';
import PropTypes from 'prop-types';

import NavbarComponent from '../Navbar/NavbarComponent';
import SectionComponent from '../Section/SectionComponent';
import '../../assets/scss/Home.css';

import {translate} from 'react-i18next';
import LoaderComponent from "../Loader/LoaderComponent";
import {CardActionsComponent, CardComponent, CardContentComponent, CardTitleComponent} from "../Card/CardComponent";

class HomeComponent extends Component {
    static propTypes = {
        t: PropTypes.func,
        i18n: PropTypes.object,
    };

    componentDidMount() {
        const {t} = this.props;
        document.title = t('homePageTitle');
    }

    render() {
        // const {t} = this.props;
        return (
            <main>
                <NavbarComponent/>
                <LoaderComponent accent/>
                <LoaderComponent primary/>
                <SectionComponent>
                    <CardComponent zIndex={1}>
                        <CardTitleComponent primaryText={"TITLE 1"}/>
                        <CardContentComponent>TESTE</CardContentComponent>
                        <CardActionsComponent/>
                    </CardComponent>
                    <br/><br/>
                    <CardComponent zIndex={2}>
                        <CardTitleComponent primaryText={"TITLE 2"}/>
                        <CardContentComponent>TESTE</CardContentComponent>
                        <CardActionsComponent/>
                    </CardComponent>
                    <br/><br/>
                    <CardComponent zIndex={3}>
                        <CardTitleComponent primaryText={"TITLE 3"}/>
                        <CardContentComponent>TESTE</CardContentComponent>
                        <CardActionsComponent/>
                    </CardComponent>
                    <br/><br/>
                    <CardComponent zIndex={4}>
                        <CardTitleComponent primaryText={"TITLE 4"}/>
                        <CardContentComponent>TESTE</CardContentComponent>
                        <CardActionsComponent/>
                    </CardComponent>
                    <br/><br/>
                    <CardComponent zIndex={5}>
                        <CardTitleComponent primaryText={"TITLE 5"}/>
                        <CardContentComponent>TESTE</CardContentComponent>
                        <CardActionsComponent/>
                    </CardComponent>
                </SectionComponent>
            </main>
        )
    }
}

export default translate('translations')(HomeComponent);
