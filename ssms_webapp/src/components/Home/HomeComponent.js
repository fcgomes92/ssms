import React, {Component} from 'react';
import PropTypes from 'prop-types';

import NavbarComponent from '../Navbar/NavbarComponent';
import SectionComponent from '../Section/SectionComponent';
import '../../assets/scss/Home.css';

import {translate} from 'react-i18next';
// import LoaderComponent from "../Loader/LoaderComponent";
// import {CardActionsComponent, CardComponent, CardContentComponent, CardTitleComponent} from "../Card/CardComponent";
import {login} from "../../actions/auth";
import ProductsListComponent from "../ProductsList/ProductsListComponent";

class HomeComponent extends Component {
    static propTypes = {
        t: PropTypes.func,
        i18n: PropTypes.object,
    };

    state = {
        email: '',
        password: '',
    };

    componentDidMount() {
        const {t} = this.props;
        document.title = t('homePageTitle');
        this.setState({token: localStorage.getItem(`token`)});
    }

    handleLoginFormSubmit = async (e) => {
        e.preventDefault();
        const {email, password} = this.state;
        try {
            let response = await login(email, password);
            localStorage.setItem('token', response.data);
            await this.setState({token: response.data})
        } catch (e) {
            alert(e)
        }
    };

    handleInputChange = (e) => {
        const {value, name} = e.target;
        this.setState({[name]: value});
    };

    renderLogin() {
        const {token} = this.state;
        if (token) {
            return null;
        }

        const {t} = this.props;
        const {email, password} = this.state;
        const cls = {
            input: `flat-input`,
            button: `flat-button flat-button--green-500`,
        };

        return (
            <SectionComponent>
                <form onSubmit={this.handleLoginFormSubmit}>
                    <label>
                        {t(`email`)}
                        <input className={cls.input} name={`email`} value={email} type={`email`} onChange={this.handleInputChange}/>
                    </label>
                    <label>
                        {t(`password`)}
                        <input className={cls.input} name={`password`} value={password} type={`password`} onChange={this.handleInputChange}/>
                    </label>
                    <button className={cls.button} type={`submit`}>{t(`login`)}</button>
                </form>
            </SectionComponent>
        )
    }

    renderProducts() {
        const {token} = this.state;
        if (!token) {
            return null;
        }

        return (
            <ProductsListComponent/>
        )
    }

    render() {
        return (
            <main>
                <NavbarComponent/>
                {/*<SectionComponent id={`loadings`}>*/}
                {/*<LoaderComponent accent/>*/}
                {/*<LoaderComponent primary/>*/}
                {/*</SectionComponent>*/}
                {/*<SectionComponent id={`cards`}>*/}
                {/*<CardComponent zIndex={1}>*/}
                {/*<CardTitleComponent primaryText={"TITLE 1"}/>*/}
                {/*<CardContentComponent>TESTE</CardContentComponent>*/}
                {/*<CardActionsComponent/>*/}
                {/*</CardComponent>*/}
                {/*<br/><br/>*/}
                {/*<CardComponent zIndex={2}>*/}
                {/*<CardTitleComponent primaryText={"TITLE 2"}/>*/}
                {/*<CardContentComponent>TESTE</CardContentComponent>*/}
                {/*<CardActionsComponent/>*/}
                {/*</CardComponent>*/}
                {/*<br/><br/>*/}
                {/*<CardComponent zIndex={3}>*/}
                {/*<CardTitleComponent primaryText={"TITLE 3"}/>*/}
                {/*<CardContentComponent>TESTE</CardContentComponent>*/}
                {/*<CardActionsComponent/>*/}
                {/*</CardComponent>*/}
                {/*<br/><br/>*/}
                {/*<CardComponent zIndex={4}>*/}
                {/*<CardTitleComponent primaryText={"TITLE 4"}/>*/}
                {/*<CardContentComponent>TESTE</CardContentComponent>*/}
                {/*<CardActionsComponent/>*/}
                {/*</CardComponent>*/}
                {/*<br/><br/>*/}
                {/*<CardComponent zIndex={5}>*/}
                {/*<CardTitleComponent primaryText={"TITLE 5"}/>*/}
                {/*<CardContentComponent>TESTE</CardContentComponent>*/}
                {/*<CardActionsComponent/>*/}
                {/*</CardComponent>*/}
                {/*</SectionComponent>*/}
                {this.renderLogin()}
                {this.renderProducts()}
            </main>
        )
    }
}

export default translate('translations')(HomeComponent);
