import React from 'react'
import './PageHeader.css'
import { OpenInNew } from '@mui/icons-material'
import logoFilmDrop from '../../../assets/logo-filmdrop-e84.png'
import { useSelector } from 'react-redux'
import { Box } from '@mui/material'
import CartButton from '../../Cart/CartButton/CartButton'
import DrawTools from '../../DrawTools/DrawTools'
import Logo from '../../../assets/taskingSprintLogo.svg'
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

        <img
          src={
            Logo
          }
          alt="FilmDrop default app logo"
          className="headerLogoImage"
        />

        <h3>Berlin Tasking Sprint 2024</h3>

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
