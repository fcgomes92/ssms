import React from 'react';

import SectionComponent from "../Section/SectionComponent";
import LoaderComponent from "../Loader/LoaderComponent";
import {createProduct, getProducts} from "../../actions/products";
import {ListComponent, ListItemComponent} from "../List/ListComponent";

export default class ProductsListComponent extends React.Component {
    state = {
        token: null,
        loading: true,
        products: [],
        productValue: 0,
        productName: '',
    };

    componentDidMount() {
        this.setState({token: localStorage.getItem(`token`)});
        this.handleLoadProducts();
    }

    handleLoadProducts = async () => {
        try {
            let response = await getProducts();
            await this.setState({products: response.data});
        } catch (e) {
            alert(e);
        }
        await this.setState({loading: false});
    };

    handleProductFormSubmit = async (e) => {
        e.preventDefault();

        const {productName, productValue, products} = this.state;
        try {
            let response = await createProduct({name: productName, value: productValue});
            this.setState({products: [...products, response.data], productName: '', productValue: 0});
        } catch (e) {
            alert(e)
        }

    };

    handleProductFormOnChangeInput = (e) => {
        const {value, name} = e.target;
        this.setState({[name]: value});
    };

    renderProductsList() {
        const {products} = this.state;
        return (
            <ListComponent>
                {
                    products.map((product, idx) => {
                        return (
                            <ListItemComponent primaryText={
                            <div style={{display: 'flex', justifyContent: 'space-between'}}>
                                <span>{product.name}</span>
                                <span>{product.code}</span>
                            </div>}
                                               leftIcon={`(${product.value})`}
                                               key={`__product-list-item-${product.id}`}/>
                        )
                    })
                }
            </ListComponent>
        )
    }

    renderProductForm() {
        const {productName, productValue} = this.state;
        return (
            <form onSubmit={this.handleProductFormSubmit}>
                <label>{`Name`}
                    <input required
                           name={`productName`}
                           value={productName}
                           onChange={this.handleProductFormOnChangeInput}/>
                </label>
                <label>{`Value`}
                    <input required
                           name={`productValue`}
                           value={productValue}
                           onChange={this.handleProductFormOnChangeInput}/>
                </label>
                <button type={`subimt`}>{`save`}</button>
            </form>
        )
    }

    render() {
        const {loading} = this.state;
        if (loading) {
            return (
                <LoaderComponent/>
            )
        }

        return (
            <SectionComponent>
                {this.renderProductsList()}
                {this.renderProductForm()}
            </SectionComponent>
        )
    }
}