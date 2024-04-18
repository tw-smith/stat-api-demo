import { Box, Switch } from '@mui/material'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { useSelector , useDispatch } from 'react-redux'
import 'react-tooltip/dist/react-tooltip.css'
import {
  setautoCenterOnItemChanged,
  setisDrawingEnabled,
  setsearchGeojsonBoundary,
  setshowSearchByGeom,
  setshowUploadGeojsonModal
} from '../../redux/slices/mainSlice'
import { clearLayer, enableMapPolyDrawing } from '../../utils/mapHelper'

const DrawTools = () => {
  const dispatch = useDispatch()
  const _appConfig = useSelector((state) => state.mainSlice.appConfig)

  const _showSearchByGeom = useSelector(
    (state) => state.mainSlice.showSearchByGeom
  )

  const _searchGeojsonBoundary = useSelector(
    (state) => state.mainSlice.searchGeojsonBoundary
  )

  const _autoCenterOnItemChanged = useSelector(
    (state) => state.mainSlice.autoCenterOnItemChanged
  )

  function onDrawBoundaryClicked() {
    if (_searchGeojsonBoundary) {
      return
    }
    dispatch(setshowSearchByGeom(!_showSearchByGeom))
    dispatch(setisDrawingEnabled(true))
    enableMapPolyDrawing()
  }

  function onUploadGeojsonButtonClicked() {
    if (_searchGeojsonBoundary) {
      return
    }
    dispatch(setshowSearchByGeom(false))
    dispatch(setshowUploadGeojsonModal(true))
  }

  function onClearButtonClicked() {
    if (!_searchGeojsonBoundary) {
      return
    }
    dispatch(setsearchGeojsonBoundary(null))
    dispatch(setshowSearchByGeom(false))
    clearLayer('drawBoundsLayer')
  }

  function updateAutoCenterState() {
    dispatch(setautoCenterOnItemChanged(!_autoCenterOnItemChanged))
  }

  const theme = createTheme({
    components: {
      MuiSwitch: {
        styleOverrides: {
          switchBase: {
            color: '#fff'
          },
          colorPrimary: {
            '&.Mui-checked': {
              color: '#fff'
            }
          },
          track: {
            backgroundColor: '#dedede',
            '.Mui-checked.Mui-checked + &': {
              backgroundColor: '#6cc24a'
            }
          }
        }
      }
    }
  })

  return (
    <div>
      {_appConfig.SEARCH_BY_GEOM_ENABLED && (
        <div className="searchContainer searchBoundary">
          <Box className="searchFilterContainer">

            <div className="searchByGeomOptionsButtons">
              <button
                className={
                  !_searchGeojsonBoundary
                    ? 'searchByGeomOptionsButton'
                    : 'searchByGeomOptionsButton ' +
                    'searchByGeomOptionsButtonDisabled'
                }
                onClick={onDrawBoundaryClicked}
              >
                Draw
              </button>
              <button
                className={
                  !_searchGeojsonBoundary
                    ? 'searchByGeomOptionsButton'
                    : 'searchByGeomOptionsButton ' +
                    'searchByGeomOptionsButtonDisabled'
                }
                onClick={onUploadGeojsonButtonClicked}
              >
                Upload
              </button>
              <button
                className={
                  _searchGeojsonBoundary
                    ? 'searchByGeomOptionsButton'
                    : 'searchByGeomOptionsButton ' +
                    'searchByGeomOptionsButtonDisabled'
                }
                onClick={onClearButtonClicked}
              >
                Clear
              </button>
            </div>
          </Box>
        </div>
      )}
    </div>
  )
}

export default DrawTools
