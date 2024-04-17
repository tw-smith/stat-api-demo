import React from 'react'
import './PageHeader.css'
import { OpenInNew } from '@mui/icons-material'
import logoFilmDrop from '../../../assets/logo-filmdrop-e84.png'
import { useSelector } from 'react-redux'
import { Box } from '@mui/material'
import CartButton from '../../Cart/CartButton/CartButton'
import DrawTools from '../../DrawTools/DrawTools'
const PageHeader = () => {
  const _appConfig = useSelector((state) => state.mainSlice.appConfig)

  function onDashboardClick() {
    window.open(_appConfig.DASHBOARD_BTN_URL, '_blank')
  }

  function onAnalyzeClick() {
    window.open(_appConfig.ANALYZE_BTN_URL, '_blank')
  }

  return (
    <div className="PageHeader" data-testid="testPageHeader">
      <div className="pageHeaderLeft">
        {_appConfig.LOGO_URL ? (
          <img
            src={_appConfig.LOGO_URL}
            alt={_appConfig.LOGO_ALT}
            className="headerLogoImage"
          ></img>
        ) : (
          <img
            src={
              _appConfig.PUBLIC_URL
                ? _appConfig.PUBLIC_URL + '/logo.png'
                : './logo.png'
            }
            alt="FilmDrop default app logo"
            className="headerLogoImage"
          />
        )}
      </div>
      <div className="pageHeaderRight">
        <DrawTools />
        {_appConfig.CART_ENABLED ? (
          <Box className="cartButtonHeaderBar">
            <CartButton></CartButton>
          </Box>
        ) : null}
      </div>
    </div>
  )
}

export default PageHeader
