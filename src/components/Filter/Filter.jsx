import {
  Box,
  FormControl,
  FormHelperText,
  Input,
  InputLabel,
  Slider,
  Stack
} from '@mui/material'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { useDispatch, useSelector } from 'react-redux'
import 'react-tooltip/dist/react-tooltip.css'
import { setshowSearchByGeom } from '../../redux/slices/mainSlice'
import { newSearch } from '../../utils/searchHelper'
import './Filter.css'

const SELECTED_PRODUCT = {
  type: 'Product',
  id: 'multispectral',
  title: 'Multispectral',
  description: 'Full color EO image',
  keywords: ['EO', 'color'],
  license: 'license',
  providers: {
    name: 'planet',
    description: 'planet description',
    roles: ['producer'],
    url: 'planet link'
  },
  links: {
    href: 'https://example.com/',
    rel: 'latest-version',
    type: 'media type',
    title: 'title'
  },
  constraints: {
    gsd: {
      minimum: 0.5,
      maximum: 10.0
    },
    target_elevation: {
      minimum: 30.0,
      maximum: 90.0
    },
    target_azimuth: {
      minimum: -360.0,
      maximum: 360.0
    },
    'view:sun_elevation': {
      minimum: 10.0,
      maximum: 90.0
    },
    'view:sun_azimuth': {
      minimum: -360.0,
      maximum: 360.0
    },
    'view:off_nadir': {
      minimum: 0.0,
      maximum: 30.0
    },
    cloud_coverage_prediction_max: {
      type: 'number',
      minimum: 0,
      maximum: 100,
      multipleOf: 0.01
    }
  },
  parameters: {
    'eo:cloud_cover': {
      type: 'number',
      minimum: 0,
      maximum: 100,
      multipleOf: 0.01
    }
  },
  properties: {
    'eo:bands': [
      {
        name: 'band1',
        common_name: 'blue',
        center_wavelength: 0.47,
        full_width_half_max: 0.07,
        solar_illumination: 1959.66
      },
      {
        name: 'band2',
        common_name: 'green',
        center_wavelength: 0.56,
        full_width_half_max: 0.08,
        solar_illumination: 1823.24
      },
      {
        name: 'band3',
        common_name: 'red',
        center_wavelength: 0.645,
        full_width_half_max: 0.09,
        solar_illumination: 1512.06
      },
      {
        name: 'band4',
        common_name: 'nir',
        center_wavelength: 0.8,
        full_width_half_max: 0.152,
        solar_illumination: 1041.63
      }
    ]
  }
}

const Filter = () => {
  const dispatch = useDispatch()
  const _selectedCollectionData = useSelector(
    (state) => state.mainSlice.selectedCollectionData
  )

  const _viewMode = useSelector((state) => state.mainSlice.viewMode)
  const _searchGeojsonBoundary = useSelector(
    (state) => state.mainSlice.searchGeojsonBoundary
  )
  const _appConfig = useSelector((state) => state.mainSlice.appConfig)
  const mosaicTilerURL = _appConfig.MOSAIC_TILER_URL || ''

  const theme = createTheme({
    components: {
      MuiFormControlLabel: {
        styleOverrides: {
          label: {
            color: '#fff'
          },
          root: {
            color: '#fff'
          }
        }
      },
      MuiFormHelperText: {
        styleOverrides: {
          root: {
            color: '#fff'
          }
        }
      },

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

  const filterContainer = []
  for (const constraintName of Object.keys(SELECTED_PRODUCT.constraints)) {
    const constraint = SELECTED_PRODUCT.constraints[constraintName]
    if (
      constraint.type === 'number' ||
      constraint.minimum !== undefined ||
      constraint.maximum !== undefined
    ) {
      filterContainer.push(
        <FormControl key={constraintName}>
          <InputLabel htmlFor="my-input" sx={{ color: '#FFF' }}>
            {constraintName}
          </InputLabel>
          <Slider disabled defaultValue={30} aria-label="Disabled slider" />
          {/* <Input id="my-input" aria-describedby="my-helper-text" onTouchMoveCapture={}/> */}
          <FormHelperText></FormHelperText>
        </FormControl>
      )
    }
  }

  function processSearchBtn() {
    newSearch()
    dispatch(setshowSearchByGeom(false))
  }

  return (
    <ThemeProvider theme={theme}>
      <div className="" data-testid="Search">
        <form>
          <Stack gap={4}>{filterContainer}</Stack>

          <div className="" style={{ marginTop: 24 }}>
            <button
              className={`actionButton searchButton`}
              onClick={() => processSearchBtn()}
              type="submit"
            >
              Search
            </button>
          </div>
        </form>
      </div>
    </ThemeProvider>
  )
}

export default Filter
