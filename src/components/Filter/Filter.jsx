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
  conformsTo: [
    'https://api.statspec.org/geojson#polygon',
    'https://api.statspec.org/geojson#multipolygon'
  ],
  id: 'umbra_archive_catalog',
  title: 'Umbra Archive Catalog',
  description:
    'Umbra SAR Images served by the Archive Catalog. Way more detail here or a link down in links to Product documentation.',
  keywords: ['SAR', 'Archive'],
  license: 'CC-BY-4.0',
  providers: {
    name: 'Umbra',
    description: 'Global Omniscience',
    roles: ['producer'],
    url: 'https://umbra.space'
  },
  links: {
    href: 'https://docs.canopy.umbra.space/',
    rel: 'documentation',
    type: 'docs',
    title: 'Canopy Documentation'
  },
  parameters: {
    description: 'Umbra Archive Catalog Parameters docstring yay!',
    properties: {
      'sar:resolution_range': {
        type: 'number',
        minimum: 0.25,
        maximum: 1,
        description:
          'The range resolution of the SAR Image. This is equivalent to the resolution of the ground plane projected GEC Cloud-Optimized Geotiff',
        title: 'Range Resolution (m)'
      },
      'sar:looks_azimuth': {
        type: 'number',
        minimum: 1,
        maximum: 10,
        description:
          'The azimuth looks in the SAR Image. This value times the sar:resolution_range gives the azimuth resolution of the complex products.',
        title: 'Range Resolution (m)'
      },
      platform: {
        description: 'The satellites to consider for this Opportunity.',
        title: 'Platform (Satellite)',
        type: 'string',
        regex: 'Umbra-\\d{2}'
      }
    },
    title: 'UmbraArchiveCatalogParameters',
    type: 'object'
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
  for (const constraintName of Object.keys(
    SELECTED_PRODUCT.parameters.properties
  )) {
    const constraint = SELECTED_PRODUCT.parameters.properties[constraintName]
    if (constraint.type === 'number') {
      filterContainer.push(
        <FormControl key={constraintName}>
          <InputLabel htmlFor={constraintName} sx={{ color: '#FFF' }}>
            {constraint.title}
          </InputLabel>
          <Slider
            id={constraintName}
            disabled
            defaultValue={30}
            aria-label="Disabled slider"
          />
          <FormHelperText>{constraint.description}</FormHelperText>
        </FormControl>
      )
      continue
    }

    if (constraint.type === 'string') {
      filterContainer.push(
        <FormControl key={constraintName}>
          <InputLabel htmlFor={constraintName} sx={{ color: '#FFF' }}>
            {constraint.title}
          </InputLabel>
          <Input
            id={constraintName}
            aria-describedby={constraintName}
          />
          <FormHelperText>{constraint.description}</FormHelperText>
        </FormControl>
      )
      continue
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
