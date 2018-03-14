import React from 'react';

import PropTypes from 'prop-types';

import {translate} from "react-i18next";

import SimpleDialogComponent from './SimpleDialogComponent';
import {CardActionsComponent, CardComponent, CardContentComponent, CardTitleComponent} from "../Card/CardComponent";
import {ListComponent, ListItemComponent} from "../List/ListComponent";

class DevelopersDialogComponent extends SimpleDialogComponent {
    static propTypes = {
        t: PropTypes.func,
        i18n: PropTypes.object,
    };

    renderContent() {
        const {t} = this.props;

        const cls = {
            actionButton: 'flat-button flat-button--transparent'
        };

        return (
            <CardComponent>
                <CardTitleComponent primaryText={t('developersDialogPrimaryTitle')}
                                    secondaryText={t('developersDialogSecondaryTitle')}/>
                {/*<CardMediaComponent srcImg={Logo}/>*/}
                <CardContentComponent>
                    <ListComponent>
                        <ListItemComponent href={t('gitHubUrl')}
                                           target="_blank"
                                           leftIcon={<i className={'ion-social-github icon--3x'}/>}
                                           primaryText={t('gitHub')}/>
                        <ListItemComponent href={t('blogUrl')}
                                           target="_blank"
                                           leftIcon={<i className={'ion-ios-world-outline icon--3x'}/>}
                                           primaryText={t('blog')}/>
                        <ListItemComponent href={t('linkedInUrl')}
                                           target="_blank"
                                           leftIcon={<i className={'ion-social-linkedin icon--3x'}/>}
                                           primaryText={t('linkedIn')}/>
                    </ListComponent>
                </CardContentComponent>
                <CardActionsComponent>
                    <button className={cls.actionButton}
                            onClick={this.handleOnRequestClose}>{t('close')}
                    </button>
                </CardActionsComponent>
            </CardComponent>
        );
    }
}

export default translate('translations')(DevelopersDialogComponent);